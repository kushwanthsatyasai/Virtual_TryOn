"""
One-off migration script to push existing local media to Cloudinary
and update database paths for Render / mobile.

Usage (from backend directory, with venv activated and CLOUDINARY_URL set):

    python migrate_media_to_cloudinary.py
"""
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from typing import Optional

import cloudinary
import cloudinary.uploader
from sqlalchemy.orm import Session

from app.models.database import get_db
from app.models import user as user_model
from app.models import tryon_history as history_model


def _config_cloudinary() -> bool:
    url = os.getenv("CLOUDINARY_URL")
    if not url or not url.strip():
        print("CLOUDINARY_URL not set. Nothing to migrate.")
        return False
    cloudinary.config(cloudinary_url=url)
    return True


def _upload_if_exists(local_path: str, public_id: str, folder: str) -> Optional[str]:
    path = Path(local_path)
    if not path.is_file():
        return None
    try:
        result = cloudinary.uploader.upload(
            str(path),
            folder=folder,
            public_id=public_id,
            overwrite=True,
        )
        return result.get("secure_url")
    except Exception as e:
        print(f"⚠ Failed to upload {local_path} -> {folder}/{public_id}: {e}")
        return None


def migrate_avatars(db: Session) -> None:
    print("Migrating user avatars to Cloudinary…")
    users = db.query(user_model.User).all()
    for user in users:
        avatar_url = getattr(user, "avatar_url", None)
        if not avatar_url or str(avatar_url).startswith("http"):
            continue
        rel_path = str(avatar_url).lstrip("/").replace("\\", "/")
        public_id = f"avatar_user_{user.id}"
        url = _upload_if_exists(rel_path, public_id, "virtue-tryon/avatars")
        if url:
            user.avatar_url = url
            db.add(user)
            print(f"  ✓ user {user.id}: {avatar_url} -> {url}")
    db.commit()


def migrate_tryon_results(db: Session) -> None:
    print("Migrating try-on results to Cloudinary…")
    rows = db.query(history_model.TryOnHistory).all()
    for row in rows:
        path = row.result_image_url
        if not path or str(path).startswith("http"):
            continue
        rel_path = str(path).lstrip("/").replace("\\", "/")
        public_id = f"result_{row.id}"
        url = _upload_if_exists(rel_path, public_id, "virtue-tryon/results")
        if url:
            row.result_image_url = url
            db.add(row)
            print(f"  ✓ history {row.id}: {path} -> {url}")
    db.commit()


def main() -> None:
    if not _config_cloudinary():
        return
    db_gen = get_db()
    db = next(db_gen)
    try:
        migrate_avatars(db)
        migrate_tryon_results(db)
    finally:
        db.close()


if __name__ == "__main__":
    main()

