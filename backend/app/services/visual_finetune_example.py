"""
Example script: fine-tune a pre-trained ResNet50 on your own fashion images.

What this shows (for reports / presentations):
- Starts from a pre-trained ImageNet model (transfer learning).
- Fine-tunes the last layer(s) on your custom clothing dataset.
- Saves a new checkpoint you can later use for visual similarity or classification.

Expected data layout (class-per-folder, like ImageFolder):
    data/finetune_visual/
        dresses/
            img001.jpg
            img002.jpg
            ...
        shirts/
            ...
        pants/
            ...

You can run this file directly:
    cd backend
    python -m app.services.visual_finetune_example
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple

import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split
from torchvision import datasets, models, transforms


@dataclass
class FineTuneConfig:
    data_dir: str = "data/finetune_visual"
    output_path: str = "models/visual_resnet50_finetuned.pth"
    batch_size: int = 16
    num_epochs: int = 5
    lr: float = 1e-4
    weight_decay: float = 1e-4
    num_workers: int = 2
    train_split: float = 0.8
    device: str = "cuda" if torch.cuda.is_available() else "cpu"


def create_dataloaders(cfg: FineTuneConfig) -> Tuple[DataLoader, DataLoader]:
    root = Path(cfg.data_dir)
    if not root.exists():
        raise FileNotFoundError(
            f"Fine-tune data directory not found: {root}. "
            f"Expected class-per-folder layout under {root}."
        )

    transform = transforms.Compose(
        [
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.RandomHorizontalFlip(),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ]
    )

    dataset = datasets.ImageFolder(root=str(root), transform=transform)
    if len(dataset) == 0:
        raise RuntimeError(f"No images found in {root}. Add data before fine-tuning.")

    n_train = int(len(dataset) * cfg.train_split)
    n_val = len(dataset) - n_train
    train_ds, val_ds = random_split(dataset, [n_train, n_val])

    train_loader = DataLoader(
        train_ds,
        batch_size=cfg.batch_size,
        shuffle=True,
        num_workers=cfg.num_workers,
        pin_memory=True,
    )
    val_loader = DataLoader(
        val_ds,
        batch_size=cfg.batch_size,
        shuffle=False,
        num_workers=cfg.num_workers,
        pin_memory=True,
    )
    return train_loader, val_loader


def build_model(num_classes: int, device: str) -> nn.Module:
    # Start from ImageNet-pretrained ResNet50 (pre-trained model)
    model = models.resnet50(weights=models.ResNet50_Weights.IMAGENET1K_V1)

    # Replace final classification layer for our fashion classes (fine-tuning head)
    in_features = model.fc.in_features
    model.fc = nn.Linear(in_features, num_classes)

    model = model.to(device)
    return model


def train_one_epoch(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    optimizer: torch.optim.Optimizer,
    device: str,
    epoch: int,
) -> float:
    model.train()
    running_loss = 0.0
    total = 0

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        batch_size = labels.size(0)
        running_loss += loss.item() * batch_size
        total += batch_size

    avg_loss = running_loss / max(total, 1)
    print(f"[Epoch {epoch}] train loss: {avg_loss:.4f}")
    return avg_loss


@torch.no_grad()
def evaluate(
    model: nn.Module,
    loader: DataLoader,
    criterion: nn.Module,
    device: str,
    epoch: int,
) -> Tuple[float, float]:
    model.eval()
    running_loss = 0.0
    total = 0
    correct = 0

    for images, labels in loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)
        outputs = model(images)
        loss = criterion(outputs, labels)

        batch_size = labels.size(0)
        running_loss += loss.item() * batch_size
        total += batch_size

        preds = outputs.argmax(dim=1)
        correct += (preds == labels).sum().item()

    avg_loss = running_loss / max(total, 1)
    acc = correct / max(total, 1)
    print(f"[Epoch {epoch}] val loss: {avg_loss:.4f}, val acc: {acc:.3f}")
    return avg_loss, acc


def run_finetune(cfg: FineTuneConfig) -> None:
    print(f"Using device: {cfg.device}")
    train_loader, val_loader = create_dataloaders(cfg)

    num_classes = len(train_loader.dataset.dataset.classes)  # type: ignore[attr-defined]
    print(f"Found {num_classes} fashion classes for fine-tuning.")

    model = build_model(num_classes=num_classes, device=cfg.device)

    criterion = nn.CrossEntropyLoss()
    optimizer = torch.optim.AdamW(
        model.parameters(),
        lr=cfg.lr,
        weight_decay=cfg.weight_decay,
    )

    best_val_acc = 0.0
    cfg_output = Path(cfg.output_path)
    cfg_output.parent.mkdir(parents=True, exist_ok=True)

    for epoch in range(1, cfg.num_epochs + 1):
        train_one_epoch(model, train_loader, criterion, optimizer, cfg.device, epoch)
        _, val_acc = evaluate(model, val_loader, criterion, cfg.device, epoch)

        if val_acc >= best_val_acc:
            best_val_acc = val_acc
            torch.save(
                {
                    "model_state_dict": model.state_dict(),
                    "num_classes": num_classes,
                    "classes": train_loader.dataset.dataset.classes,  # type: ignore[attr-defined]
                },
                cfg_output,
            )
            print(f"  ↳ Saved best checkpoint to {cfg_output} (acc={best_val_acc:.3f})")

    print("Fine-tuning complete.")
    print(f"Best validation accuracy: {best_val_acc:.3f}")
    print(f"Checkpoint path: {cfg.output_path}")


if __name__ == "__main__":
    config = FineTuneConfig()
    run_finetune(config)

