"""
Fine-tuning on Kaggle Virtual Try-On Dataset
============================================

This script shows HOW we fine-tune a pre-trained ResNet50 using the
Kaggle Virtual Try-On Dataset:

  https://www.kaggle.com/datasets/adarshsingh0903/virtual-tryon-dataset/

Idea:
- Each sample has a PERSON image and a CLOTH image that belong together.
- We start from ImageNet-pretrained ResNet50.
- We train its embedding so that person and cloth from the same pair
  get similar feature vectors (metric learning style).

You can show this file as your fine-tuning code.

Expected local layout after downloading & extracting Kaggle data:

    data/kaggle_virtual_tryon/
        person/
            00001.jpg
            00002.jpg
            ...
        cloth/
            00001.jpg
            00002.jpg
            ...

The script:
- Finds filenames that exist in BOTH person/ and cloth/.
- Loads paired images.
- Fine-tunes ResNet50 embeddings so person–cloth pairs are close.
- Saves a checkpoint with the adapted weights.

Run from backend root:

    cd backend
    python -m app.services.kaggle_vton_finetune
"""

from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple

import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from torchvision import models, transforms
from PIL import Image


@dataclass
class KaggleVTONConfig:
    # Root directory containing "person" and "cloth" folders from the Kaggle dataset
    root_dir: str = "data/kaggle_virtual_tryon"
    batch_size: int = 8
    num_epochs: int = 5
    lr: float = 1e-4
    weight_decay: float = 1e-4
    num_workers: int = 2
    image_size: int = 224
    device: str = "cuda" if torch.cuda.is_available() else "cpu"
    output_path: str = "models/kaggle_vton_resnet50_finetuned.pth"


class KaggleVTONPairDataset(Dataset):
    """
    Dataset of (person_image, cloth_image) pairs from the Kaggle Virtual Try-On dataset.

    It expects:
        root/person/*.jpg
        root/cloth/*.jpg
    and pairs images by matching filename (e.g. 00001.jpg in both folders).
    """

    def __init__(self, cfg: KaggleVTONConfig):
        self.cfg = cfg
        root = Path(cfg.root_dir)
        self.person_dir = root / "person"
        self.cloth_dir = root / "cloth"

        if not self.person_dir.exists():
            raise FileNotFoundError(f"Person directory not found: {self.person_dir}")
        if not self.cloth_dir.exists():
            raise FileNotFoundError(f"Cloth directory not found: {self.cloth_dir}")

        exts = {".jpg", ".jpeg", ".png"}
        person_files = {
            p.name for p in self.person_dir.iterdir() if p.suffix.lower() in exts
        }
        cloth_files = {
            p.name for p in self.cloth_dir.iterdir() if p.suffix.lower() in exts
        }
        self.common = sorted(person_files & cloth_files)

        if not self.common:
            raise RuntimeError(
                f"No matching person/cloth filenames found under {self.person_dir} and {self.cloth_dir}."
            )

        self.transform = transforms.Compose(
            [
                transforms.Resize(int(cfg.image_size * 1.1)),
                transforms.CenterCrop(cfg.image_size),
                transforms.RandomHorizontalFlip(),
                transforms.ToTensor(),
                transforms.Normalize(
                    mean=[0.485, 0.456, 0.406],
                    std=[0.229, 0.224, 0.225],
                ),
            ]
        )

    def __len__(self) -> int:
        return len(self.common)

    def _load_img(self, path: Path) -> torch.Tensor:
        img = Image.open(path).convert("RGB")
        return self.transform(img)

    def __getitem__(self, idx: int):
        fname = self.common[idx]
        person_path = self.person_dir / fname
        cloth_path = self.cloth_dir / fname

        person = self._load_img(person_path)
        cloth = self._load_img(cloth_path)

        return {
            "person": person,
            "cloth": cloth,
            "id": fname,
        }


class ResNetEmbedding(nn.Module):
    """
    ResNet50 encoder returning a normalized 2048-d embedding.
    Starts from ImageNet-pretrained weights (transfer learning).
    """

    def __init__(self):
        super().__init__()
        base = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)
        modules = list(base.children())[:-1]  # remove final FC
        self.encoder = nn.Sequential(*modules)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = self.encoder(x)  # (B, 2048, 1, 1)
        x = x.view(x.size(0), -1)  # (B, 2048)
        x = nn.functional.normalize(x, dim=1)
        return x


class PairEmbeddingModel(nn.Module):
    """
    Shared encoder for person and cloth images.
    We fine-tune this encoder so that embeddings of matching pairs are close.
    """

    def __init__(self):
        super().__init__()
        self.encoder = ResNetEmbedding()

    def forward(self, person: torch.Tensor, cloth: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]:
        e_person = self.encoder(person)
        e_cloth = self.encoder(cloth)
        return e_person, e_cloth


def pair_loss(e_person: torch.Tensor, e_cloth: torch.Tensor) -> torch.Tensor:
    """
    Simple metric learning loss:
    - maximize cosine similarity between person and cloth embeddings
    """
    # cosine similarity in [-1, 1], we want it close to 1
    cos_sim = (e_person * e_cloth).sum(dim=1)
    loss = (1.0 - cos_sim).mean()
    return loss


def train(cfg: KaggleVTONConfig) -> None:
    print(f"[Kaggle VTON finetune] Using device: {cfg.device}")

    dataset = KaggleVTONPairDataset(cfg)
    loader = DataLoader(
        dataset,
        batch_size=cfg.batch_size,
        shuffle=True,
        num_workers=cfg.num_workers,
        pin_memory=True,
    )

    model = PairEmbeddingModel().to(cfg.device)
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg.lr,
        weight_decay=cfg.weight_decay,
    )

    model.train()
    global_step = 0

    for epoch in range(1, cfg.num_epochs + 1):
        running_loss = 0.0
        total = 0

        for batch in loader:
            person = batch["person"].to(cfg.device, non_blocking=True)
            cloth = batch["cloth"].to(cfg.device, non_blocking=True)

            optimizer.zero_grad()
            e_person, e_cloth = model(person, cloth)
            loss = pair_loss(e_person, e_cloth)
            loss.backward()
            optimizer.step()

            bsz = person.size(0)
            running_loss += loss.item() * bsz
            total += bsz
            global_step += 1

            if global_step % 50 == 0:
                print(
                    f"[epoch {epoch} step {global_step}] "
                    f"batch_loss={loss.item():.4f}"
                )

        avg_loss = running_loss / max(total, 1)
        print(f"[epoch {epoch}] avg_loss={avg_loss:.4f}")

    # Save fine-tuned encoder checkpoint
    out_path = Path(cfg.output_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save({"model_state_dict": model.state_dict()}, out_path)
    print(f"Saved fine-tuned model to {out_path}")


if __name__ == "__main__":
    cfg = KaggleVTONConfig()
    train(cfg)

