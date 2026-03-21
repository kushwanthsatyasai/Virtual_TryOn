"""
Prepare a MediaPipe-Pose-style keypoint dataset from CP-VTON+.

Why this exists:
- Your current try-on pipeline uses MediaPipe Pose for keypoints during inference.
- CP-VTON+ already provides OpenPose keypoints, but if you want your pose
  component to align with MediaPipe, you can export MediaPipe landmarks
  from the same CP-VTON+ images.

What this script does:
1. Reads CP-VTON+ `data_list` (train_pairs.txt / test_pairs.txt) to get person images.
2. Runs MediaPipe Pose (static image mode) on each person image.
3. Exports:
   - `pose_manifest.jsonl` with per-image keypoints
   - a COCO-like keypoints JSON (`annotations/coco_keypoints.json`)

Output keypoints:
- 33 landmarks from MediaPipe Pose.
- Stored as COCO-style `[x, y, v]` triples:
    v=0 not labeled, v=1 labeled but not visible, v=2 visible
  where visibility comes from MediaPipe's `landmark.visibility`.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Optional

import numpy as np


@dataclass(frozen=True)
class MediaPipePosePrepareConfig:
    cpvtonplus_root: Path
    split: str
    data_list: str
    out_root: Path
    visibility_threshold: float = 0.5
    copy_images: bool = False
    symlink_images: bool = False
    max_images: Optional[int] = None


def _read_data_list(data_list_path: Path) -> Iterable[str]:
    """
    CP-VTON+ `train_pairs.txt` format:
      <im_name> <cloth_name>
    We only need im_name for pose extraction.
    """
    with data_list_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            im_name, _cloth_name = line.split()
            yield im_name


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _copy_or_link(src: Path, dst: Path, *, copy_images: bool, symlink_images: bool) -> Path:
    if dst.exists():
        return dst
    _ensure_dir(dst.parent)

    if copy_images:
        shutil.copy2(src, dst)
        return dst
    if symlink_images:
        try:
            os.symlink(src, dst)
            return dst
        except OSError:
            shutil.copy2(src, dst)
            return dst

    return src


def _extract_landmarks_px(
    image_bgr: "np.ndarray",
    pose: object,
    *,
    visibility_threshold: float,
) -> tuple[np.ndarray, np.ndarray]:
    """
    Returns:
      keypoints_xy: (33, 2) pixel coords
      keypoints_v: (33,) coco visibility flags {0,1,2}
    """
    import cv2

    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    h, w = image_rgb.shape[:2]
    res = pose.process(image_rgb)

    if not res.pose_landmarks:
        # All unlabeled
        return np.zeros((33, 2), dtype=np.float32), np.zeros((33,), dtype=np.int64)

    keypoints_xy = np.zeros((33, 2), dtype=np.float32)
    keypoints_v = np.zeros((33,), dtype=np.int64)

    for i, lm in enumerate(res.pose_landmarks.landmark):
        x_px = lm.x * w
        y_px = lm.y * h
        keypoints_xy[i, 0] = float(x_px)
        keypoints_xy[i, 1] = float(y_px)

        # coco: 2 visible, 1 labeled but not visible, 0 not labeled
        vis = float(getattr(lm, "visibility", 0.0) or 0.0)
        if vis >= visibility_threshold:
            keypoints_v[i] = 2
        else:
            # If Mediapipe produced a landmark, we treat it as labeled but not visible.
            keypoints_v[i] = 1

    return keypoints_xy, keypoints_v


def prepare_dataset(cfg: MediaPipePosePrepareConfig) -> None:
    try:
        import cv2  # noqa: F401
    except ImportError as e:
        raise ImportError("This script needs `opencv-python` and `mediapipe`. Install them first.") from e
    try:
        import mediapipe as mp
    except ImportError as e:
        raise ImportError("This script needs `mediapipe`. Install it first.") from e

    split_root = cfg.cpvtonplus_root / cfg.split
    image_dir = split_root / "image"
    data_list_path = cfg.cpvtonplus_root / cfg.data_list

    if not data_list_path.exists():
        raise FileNotFoundError(f"data_list not found: {data_list_path}")
    if not image_dir.exists():
        raise FileNotFoundError(f"image dir not found: {image_dir}")

    out_split_dir = cfg.out_root / cfg.split
    out_images_dir = out_split_dir / "images"
    out_split_json_dir = out_split_dir / "annotations"
    _ensure_dir(out_images_dir)
    _ensure_dir(out_split_json_dir)

    manifest_path = out_split_dir / "pose_manifest.jsonl"
    coco_path = out_split_json_dir / "coco_keypoints.json"
    if manifest_path.exists():
        manifest_path.unlink()
    if coco_path.exists():
        coco_path.unlink()

    images = []
    annotations = []

    missing = 0
    saved = 0
    img_id = 1
    ann_id = 1

    mp_pose = mp.solutions.pose
    with mp_pose.Pose(static_image_mode=True, model_complexity=2) as pose:
        with manifest_path.open("w", encoding="utf-8") as man_f:
            for im_idx, im_name in enumerate(_read_data_list(data_list_path)):
                if cfg.max_images is not None and saved >= cfg.max_images:
                    break

                img_path = image_dir / im_name
                if not img_path.exists():
                    missing += 1
                    continue

                # Load with cv2 for MediaPipe
                import cv2

                image_bgr = cv2.imread(str(img_path))
                if image_bgr is None:
                    missing += 1
                    continue

                keypoints_xy, keypoints_v = _extract_landmarks_px(
                    image_bgr,
                    pose,
                    visibility_threshold=cfg.visibility_threshold,
                )

                keypoints_flat = np.concatenate([keypoints_xy, keypoints_v[:, None]], axis=1).reshape(-1).tolist()

                visible = keypoints_v == 2
                if np.any(visible):
                    xs = keypoints_xy[visible, 0]
                    ys = keypoints_xy[visible, 1]
                    x_min = float(xs.min())
                    y_min = float(ys.min())
                    bbox = [x_min, y_min, float(xs.max() - xs.min()), float(ys.max() - ys.min())]
                else:
                    bbox = [0.0, 0.0, 0.0, 0.0]

                if cfg.copy_images or cfg.symlink_images:
                    out_img_path = out_images_dir / im_name
                    img_manifest_path = _copy_or_link(
                        img_path,
                        out_img_path,
                        copy_images=cfg.copy_images,
                        symlink_images=cfg.symlink_images,
                    )
                else:
                    img_manifest_path = img_path

                images.append(
                    {
                        "id": img_id,
                        "file_name": str(img_manifest_path),
                        "width": int(image_bgr.shape[1]),
                        "height": int(image_bgr.shape[0]),
                    }
                )
                annotations.append(
                    {
                        "id": ann_id,
                        "image_id": img_id,
                        "category_id": 1,
                        "bbox": bbox,
                        "area": float(max(0.0, bbox[2]) * max(0.0, bbox[3])),
                        "iscrowd": 0,
                        "keypoints": keypoints_flat,
                        "num_keypoints": int(np.sum(keypoints_v > 0)),
                    }
                )

                man_f.write(
                    json.dumps(
                        {
                            "image": str(img_path),
                            "keypoints_xy": keypoints_xy.tolist(),
                            "keypoints_v": keypoints_v.tolist(),
                        }
                    )
                    + "\n"
                )

                saved += 1
                img_id += 1
                ann_id += 1

    coco = {
        "info": {"description": "CP-VTON+ images exported with MediaPipe Pose landmarks (33 keypoints)."},
        "licenses": [],
        "images": images,
        "annotations": annotations,
        "categories": [
            {
                "id": 1,
                "name": "person",
                "keypoints": [f"kpt_{i}" for i in range(33)],
                "skeleton": [],
            }
        ],
    }
    coco_path.write_text(json.dumps(coco, indent=2), encoding="utf-8")

    print(f"[mediapipe-pose-data] split={cfg.split} saved={saved} missing={missing}")
    print(f"[mediapipe-pose-data] wrote: {manifest_path}")
    print(f"[mediapipe-pose-data] wrote: {coco_path}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--cpvtonplus_root", required=True, help="Path to CP-VTON+ root (contains train/ and test/).")
    ap.add_argument("--split", default="train", choices=["train", "test"])
    ap.add_argument("--data_list", default="train_pairs.txt", help="train_pairs.txt / test_pairs.txt location inside root.")
    ap.add_argument("--out_root", default="data/mediapipe_pose_from_cpvtonplus", help="Where to write exported keypoints.")
    ap.add_argument("--visibility_threshold", type=float, default=0.5, help="Visibility threshold for coco v=2.")
    ap.add_argument("--copy_images", action="store_true", help="Copy images into output folder.")
    ap.add_argument("--symlink_images", action="store_true", help="Symlink images into output folder (may fall back).")
    ap.add_argument("--max_images", type=int, default=None, help="Limit number of exported images (debug).")
    args = ap.parse_args()

    cfg = MediaPipePosePrepareConfig(
        cpvtonplus_root=Path(args.cpvtonplus_root),
        split=args.split,
        data_list=args.data_list,
        out_root=Path(args.out_root),
        visibility_threshold=float(args.visibility_threshold),
        copy_images=bool(args.copy_images),
        symlink_images=bool(args.symlink_images),
        max_images=args.max_images,
    )
    prepare_dataset(cfg)


if __name__ == "__main__":
    main()

