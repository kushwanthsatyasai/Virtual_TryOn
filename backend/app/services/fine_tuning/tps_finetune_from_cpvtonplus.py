"""
Prepare TPS/GMM (geometric matching) training pairs from CP-VTON+.

Why this exists:
- In CP-VTON+/VITON-family methods, the TPS (or a geometric matching module)
  learns to warp a garment to match the person.
- CP-VTON+ provides the supervision you need:
  - source garment:  cloth/{c_name}
  - source garment mask: cloth-mask/{c_name}
  - target warped garment: warp-cloth/{im_name} (for TOM stage)
  - target warped mask: warp-mask/{im_name}

What this script does:
1. Reads CP-VTON+ `data_list` (train_pairs.txt / test_pairs.txt).
2. Creates a manifest file listing the paths for training a TPS/GMM model.

This script does not implement TPS training by itself. It standardizes the
dataset layout for whichever TPS/GMM training code you use.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class TPSPrepareConfig:
    cpvtonplus_root: Path
    split: str
    data_list: str
    out_root: Path
    include_tom_warp_supervision: bool = True


def _read_data_list(data_list_path: Path) -> Iterable[tuple[str, str]]:
    # Each line: <im_name> <cloth_name>
    with data_list_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            im_name, cloth_name = line.split()
            yield im_name, cloth_name


def prepare_dataset(cfg: TPSPrepareConfig) -> None:
    split_root = cfg.cpvtonplus_root / cfg.split
    cloth_dir = split_root / "cloth"
    cloth_mask_dir = split_root / "cloth-mask"
    image_dir = split_root / "image"

    warp_cloth_dir = split_root / "warp-cloth"
    warp_mask_dir = split_root / "warp-mask"

    data_list_path = cfg.cpvtonplus_root / cfg.data_list
    if not data_list_path.exists():
        raise FileNotFoundError(f"data_list not found: {data_list_path}")
    if not cloth_dir.exists():
        raise FileNotFoundError(f"cloth dir not found: {cloth_dir}")
    if not cloth_mask_dir.exists():
        raise FileNotFoundError(f"cloth-mask dir not found: {cloth_mask_dir}")
    if not image_dir.exists():
        raise FileNotFoundError(f"image dir not found: {image_dir}")

    if cfg.include_tom_warp_supervision and (not warp_cloth_dir.exists() or not warp_mask_dir.exists()):
        raise FileNotFoundError(
            f"warp dirs not found. Need TOM supervision:\n"
            f"  warp-cloth: {warp_cloth_dir}\n"
            f"  warp-mask: {warp_mask_dir}"
        )

    out_split_dir = cfg.out_root / cfg.split
    out_split_dir.mkdir(parents=True, exist_ok=True)
    manifest_path = out_split_dir / "tps_pairs.jsonl"
    if manifest_path.exists():
        manifest_path.unlink()

    written = 0
    missing = 0
    with manifest_path.open("w", encoding="utf-8") as f:
        for im_name, cloth_name in _read_data_list(data_list_path):
            person_img = image_dir / im_name
            source_cloth = cloth_dir / cloth_name
            source_cloth_mask = cloth_mask_dir / cloth_name

            if not person_img.exists() or not source_cloth.exists() or not source_cloth_mask.exists():
                missing += 1
                continue

            entry = {
                "person_image": str(person_img),
                "source_cloth": str(source_cloth),
                "source_cloth_mask": str(source_cloth_mask),
                "im_name": im_name,
                "c_name": cloth_name,
            }

            if cfg.include_tom_warp_supervision:
                target_warp_cloth = warp_cloth_dir / im_name
                target_warp_mask = warp_mask_dir / im_name
                if not target_warp_cloth.exists() or not target_warp_mask.exists():
                    missing += 1
                    continue
                entry["target_warp_cloth"] = str(target_warp_cloth)
                entry["target_warp_mask"] = str(target_warp_mask)

            f.write(json.dumps(entry) + "\n")
            written += 1

    print(f"[tps-data] split={cfg.split} written={written} missing={missing}")
    print(f"[tps-data] wrote: {manifest_path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpvtonplus_root", required=True, help="Path to CP-VTON+ root (contains train/ and test/).")
    ap.add_argument("--split", default="train", choices=["train", "test"])
    ap.add_argument("--data_list", default="train_pairs.txt", help="train_pairs.txt / test_pairs.txt location inside root.")
    ap.add_argument("--out_root", default="data/tps_from_cpvtonplus", help="Where to write TPS pairing manifest.")
    ap.add_argument("--no_tom_supervision", action="store_true", help="Skip warp-cloth/warp-mask supervision (weaker).")
    args = ap.parse_args()

    cfg = TPSPrepareConfig(
        cpvtonplus_root=Path(args.cpvtonplus_root),
        split=args.split,
        data_list=args.data_list,
        out_root=Path(args.out_root),
        include_tom_warp_supervision=not bool(args.no_tom_supervision),
    )
    prepare_dataset(cfg)


if __name__ == "__main__":
    main()

