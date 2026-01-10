from __future__ import annotations

import json
import uuid
from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps

from photokinthesis.photo import Photo


def _normalize_image(image_bytes: bytes) -> bytes:
    """Apply EXIF orientation to pixels and return clean image bytes.

    This reads the EXIF orientation tag, rotates/flips the image pixels
    accordingly, and returns a new JPEG with no EXIF orientation tag.
    """
    img = Image.open(BytesIO(image_bytes))
    img = ImageOps.exif_transpose(img)

    buffer = BytesIO()
    img.save(buffer, format="JPEG", quality=95)
    return buffer.getvalue()


class Collection:
    """Represents a collection of photos."""

    def __init__(self, name: str, photos: list[Photo]) -> None:
        self._name = name
        self._photos = photos

    @property
    def name(self) -> str:
        return self._name

    @property
    def photos(self) -> list[Photo]:
        return self._photos

    @staticmethod
    def read(path: Path) -> "Collection":
        with open(path / "collection.json") as f:
            data = json.load(f)

        photos = []
        for photo_data in data["photos"]:
            images = {
                "front": (path / photo_data["images"]["front"]).read_bytes(),
                "back": (path / photo_data["images"]["back"]).read_bytes() if "back" in photo_data["images"] else None,
                "enhanced_front": (path / photo_data["images"]["enhanced_front"]).read_bytes() if "enhanced_front" in photo_data["images"] else None,
                "thumbnail": (path / photo_data["images"]["thumbnail"]).read_bytes() if "thumbnail" in photo_data["images"] else None,
                "front_orientation": photo_data["images"].get("front_orientation", 0),
                "back_orientation": photo_data["images"].get("back_orientation", 0),
                "enhanced_front_orientation": photo_data["images"].get("enhanced_front_orientation", 0),
            }
            photo = Photo({
                "id": photo_data["id"],
                "images": images,
                "source_filenames": photo_data["source_filenames"],
            })
            photos.append(photo)

        return Collection(data["name"], photos)

    @staticmethod
    def read_fast_foto_tree(path: Path, name: str) -> "Collection":
        # Group files by directory + basename to handle collisions
        groups: dict[Path, dict[str, Path]] = {}

        for file in path.glob("**/*.jpg"):
            stem = file.stem
            if stem.endswith("_a"):
                basename = stem[:-2]
                key = "enhanced_front"
            elif stem.endswith("_b"):
                basename = stem[:-2]
                key = "back"
            else:
                basename = stem
                key = "front"

            # Use parent directory + basename as unique key
            group_key = file.parent / basename
            if group_key not in groups:
                groups[group_key] = {}
            groups[group_key][key] = file

        # Build Photo objects
        photos = []
        for group_key, files in sorted(groups.items()):
            if "front" not in files:
                continue  # Skip incomplete groups

            # Normalize images by applying EXIF orientation to pixels
            images = {
                "front": _normalize_image(files["front"].read_bytes()),
                "back": _normalize_image(files["back"].read_bytes()) if "back" in files else None,
                "enhanced_front": _normalize_image(files["enhanced_front"].read_bytes()) if "enhanced_front" in files else None,
            }

            photo = Photo({
                "id": uuid.uuid4().hex[:16],
                "images": images,
                "source_filenames": [str(f) for f in files.values()],
            })
            photo.add_thumbnail()
            photos.append(photo)

        return Collection(name, photos)

    def write(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        images_dir = path / "images"
        images_dir.mkdir(exist_ok=True)

        photos_json = []
        for photo in self._photos:
            photo_id = photo.id
            images = photo.images

            # Create subdirectory for this photo
            photo_dir = images_dir / photo_id
            photo_dir.mkdir(exist_ok=True)

            # Write image files
            image_paths = {}
            front_path = f"images/{photo_id}/front.jpg"
            (path / front_path).write_bytes(images.front)
            image_paths["front"] = front_path

            if images.back:
                back_path = f"images/{photo_id}/back.jpg"
                (path / back_path).write_bytes(images.back)
                image_paths["back"] = back_path

            if images.enhanced_front:
                enhanced_path = f"images/{photo_id}/enhanced_front.jpg"
                (path / enhanced_path).write_bytes(images.enhanced_front)
                image_paths["enhanced_front"] = enhanced_path

            if images.thumbnail:
                thumbnail_path = f"images/{photo_id}/thumbnail.jpg"
                (path / thumbnail_path).write_bytes(images.thumbnail)
                image_paths["thumbnail"] = thumbnail_path

            image_paths["front_orientation"] = images.front_orientation
            image_paths["back_orientation"] = images.back_orientation
            image_paths["enhanced_front_orientation"] = images.enhanced_front_orientation

            photos_json.append({
                "id": photo_id,
                "images": image_paths,
                "source_filenames": photo.source_filenames,
            })

        collection_data = {
            "name": self._name,
            "photos": photos_json,
        }

        with open(path / "collection.json", "w") as f:
            json.dump(collection_data, f, indent=2)

