"""
Prepare U2-Net-style segmentation training data from CP-VTON+.

Why this exists:
- CP-VTON+ preprocessed data already contains human parsing maps
  (e.g. `image-parse-new/*.png`) and body masks (`image-mask/*.png`).
- If you want to claim you fine-tuned your U2-Net, you need pixel-wise
  supervision. These parsing maps are exactly that supervision.

What this script does:
1. Reads CP-VTON+ `data_list` (train_pairs.txt / test_pairs.txt).
2. For each person image name, loads its parsing mask from:
      <cpvtonplus_root>/<split>/image-parse-new/<im_name>.png
3. Converts parsing into a binary mask for "upper-clothes" supervision
   using CP-VTON+ label ids:
      5=UpperClothes, 6=Dress, 7=Coat
4. Writes a lightweight dataset manifest:
      <out_root>/<split>/pairs.txt
   Each line: "<image_path> <mask_path>"

Notes:
- This script prepares data only (it does not implement the U2-Net model itself).
- Keep the U2-Net training code in a separate repo/framework if you already
  have one (e.g., U-2-Net official repo). This file makes the dataset consistent.
"""

from __future__ import annotations

import argparse
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

import numpy as np
from PIL import Image


@dataclass(frozen=True)
class U2NetPrepareConfig:
    cpvtonplus_root: Path
    split: str
    data_list: str
    out_root: Path
    upper_clothes_ids: Sequence[int] = (5, 6, 7)
    copy_images: bool = False
    symlink_images: bool = False


def _read_data_list(data_list_path: Path) -> Iterable[tuple[str, str]]:
    """
    CP-VTON+ `train_pairs.txt` format:
      <im_name> <cloth_name>
    """
    with data_list_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            im_name, cloth_name = line.split()
            yield im_name, cloth_name


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _copy_or_link(src: Path, dst: Path, *, copy_images: bool, symlink_images: bool) -> None:
    if dst.exists():
        return
    _ensure_dir(dst.parent)

    if copy_images:
        shutil.copy2(src, dst)
        return
    if symlink_images:
        try:
            os.symlink(src, dst)
            return
        except OSError:
            # Windows can fail symlinks depending on permissions; fall back to copy.
            shutil.copy2(src, dst)
            return

    # Default mode: write manifest that points to the original image path.
    # We keep dst unused.
    return


def _build_upper_clothes_mask(parse_mask_png: Path, upper_clothes_ids: Sequence[int]) -> Image.Image:
    parse_img = Image.open(parse_mask_png).convert("L")
    parse_array = np.array(parse_img, dtype=np.uint8)
    upper = np.isin(parse_array, np.array(list(upper_clothes_ids), dtype=np.uint8))
    mask = (upper.astype(np.uint8) * 255)
    return Image.fromarray(mask, mode="L")


def prepare_dataset(cfg: U2NetPrepareConfig) -> None:
    split_root = cfg.cpvtonplus_root / cfg.split
    image_dir = split_root / "image"
    parse_dir = split_root / "image-parse-new"
    data_list_path = cfg.cpvtonplus_root / cfg.data_list

    if not data_list_path.exists():
        raise FileNotFoundError(f"data_list not found: {data_list_path}")
    if not image_dir.exists():
        raise FileNotFoundError(f"image dir not found: {image_dir}")
    if not parse_dir.exists():
        raise FileNotFoundError(f"image-parse-new dir not found: {parse_dir}")

    out_split_dir = cfg.out_root / cfg.split
    out_masks_dir = out_split_dir / "masks"
    _ensure_dir(out_masks_dir)

    pairs_path = out_split_dir / "pairs.txt"
    if pairs_path.exists():
        pairs_path.unlink()

    missing_count = 0
    total = 0
    with pairs_path.open("w", encoding="utf-8") as f:
        for im_name, _cloth_name in _read_data_list(data_list_path):
            total += 1

            img_path = image_dir / im_name
            parse_png_name = im_name.replace(".jpg", ".png")
            parse_mask_png = parse_dir / parse_png_name

            if not img_path.exists() or not parse_mask_png.exists():
                missing_count += 1
                continue

            mask_img = _build_upper_clothes_mask(parse_mask_png, cfg.upper_clothes_ids)

            out_mask_path = out_masks_dir / parse_png_name
            mask_img.save(out_mask_path, format="PNG")

            if cfg.copy_images or cfg.symlink_images:
                out_images_dir = out_split_dir / "images"
                _ensure_dir(out_images_dir)
                out_img_path = out_images_dir / im_name
                _copy_or_link(
                    img_path,
                    out_img_path,
                    copy_images=cfg.copy_images,
                    symlink_images=cfg.symlink_images,
                )
                img_manifest_path = out_img_path
            else:
                img_manifest_path = img_path

            f.write(f"{img_manifest_path} {out_mask_path}\n")

    print(f"[u2net-data] split={cfg.split} total_pairs={total} missing={missing_count}")
    print(f"[u2net-data] wrote: {pairs_path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpvtonplus_root", required=True, help="Path to CP-VTON+ root (contains train/ and test/).")
    ap.add_argument("--split", default="train", choices=["train", "test"], help="Which split to export.")
    ap.add_argument("--data_list", default="train_pairs.txt", help="train_pairs.txt / test_pairs.txt location inside root.")
    ap.add_argument("--out_root", default="data/u2net_from_cpvtonplus", help="Where to write exported masks and pairs.txt.")
    ap.add_argument("--copy_images", action="store_true", help="Copy images into output folder.")
    ap.add_argument("--symlink_images", action="store_true", help="Symlink images into output folder (Windows may fall back to copy).")
    args = ap.parse_args()

    cfg = U2NetPrepareConfig(
        cpvtonplus_root=Path(args.cpvtonplus_root),
        split=args.split,
        data_list=args.data_list,
        out_root=Path(args.out_root),
        copy_images=bool(args.copy_images),
        symlink_images=bool(args.symlink_images),
    )
    prepare_dataset(cfg)


if __name__ == "__main__":
    main()

