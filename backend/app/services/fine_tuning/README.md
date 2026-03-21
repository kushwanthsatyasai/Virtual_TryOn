# Fine-tuning: where to get datasets

Scripts in this folder **prepare** training data (masks, pose keypoints, TPS pair lists). You download datasets from the links below and point `--cpvtonplus_root` at the extracted CP-VTON+ folder.

| Goal | Dataset | Download |
|------|---------|----------|
| U2-Net / parsing-style masks, TPS pairs, (optional) pose JSON | **CP-VTON+** preprocessed | [OneDrive – CP-VTON+ data](https://1drv.ms/u/s!Ai8t8GAHdzVUiQQYX0azYhqIDPP6?e=4cpFTI) |
| MediaPipe pose export | Same person images as above (script runs MediaPipe on `train/image/`) | Same root as CP-VTON+ |
| Metric learning / embeddings (separate script) | Kaggle VTON pairs | [Kaggle – Virtual Try-On Dataset](https://www.kaggle.com/datasets/adarshsingh0903/virtual-tryon-dataset/) |
| Human parsing (optional, not in this repo’s CP flow) | LIP | [LIP dataset page](http://www.sysu-hcp.net/lip/) |
| General pose keypoints (optional) | COCO Keypoints | [COCO downloads](http://cocodataset.org/#download) |

After extracting CP-VTON+, you should see `train/` and `test/` with subfolders like `image`, `cloth`, `image-parse-new`, `pose` (OpenPose JSON — not required for the MediaPipe script), `warp-cloth`, `warp-mask`, and `train_pairs.txt` at the dataset root.

Example (from `backend/`):

```bash
python -m app.services.fine_tuning.u2net_finetune_from_cpvtonplus --cpvtonplus_root "D:/data/cpvtonplus" --split train
python -m app.services.fine_tuning.mediapipe_pose_finetune_from_cpvtonplus --cpvtonplus_root "D:/data/cpvtonplus" --split train --max_images 500
python -m app.services.fine_tuning.tps_finetune_from_cpvtonplus --cpvtonplus_root "D:/data/cpvtonplus" --split train
```
