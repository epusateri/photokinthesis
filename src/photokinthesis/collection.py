import json
import uuid
from pathlib import Path


class Collection:
    """Represents a collection of photos."""

    def __init__(self, data: dict) -> None:
        self._name = data["name"]
        self._photos = data["photos"]

    @staticmethod
    def read(path: Path) -> "Collection":
        with open(path / "collection.json") as f:
            data = json.load(f)

        photos = []
        for photo in data["photos"]:
            images = {
                "front": (path / photo["images"]["front"]).read_bytes(),
                "back": (path / photo["images"]["back"]).read_bytes() if "back" in photo["images"] else None,
                "enhanced_front": (path / photo["images"]["enhanced_front"]).read_bytes() if "enhanced_front" in photo["images"] else None,
            }
            photos.append({
                "id": photo["id"],
                "images": images,
                "source_filenames": photo["source_filenames"],
            })

        return Collection({"name": data["name"], "photos": photos})

    @staticmethod
    def read_fast_foto_tree(path: Path, name: str) -> "Collection":
        # Group files by directory + basename to handle collisions
        groups: dict[Path, dict[str, Path]] = {}

        for file in path.glob("**/*.jpg"):
            name = file.stem
            if name.endswith("_a"):
                basename = name[:-2]
                key = "enhanced_front"
            elif name.endswith("_b"):
                basename = name[:-2]
                key = "back"
            else:
                basename = name
                key = "front"

            # Use parent directory + basename as unique key
            group_key = file.parent / basename
            if group_key not in groups:
                groups[group_key] = {}
            groups[group_key][key] = file

        # Build photo data list
        photos = []
        for group_key, files in sorted(groups.items()):
            if "front" not in files:
                continue  # Skip incomplete groups

            images = {
                "front": files["front"].read_bytes(),
                "back": files["back"].read_bytes() if "back" in files else None,
                "enhanced_front": files["enhanced_front"].read_bytes() if "enhanced_front" in files else None,
            }

            photos.append({
                "id": uuid.uuid4().hex[:16],
                "images": images,
                "source_filenames": [str(f) for f in files.values()],
            })

        return Collection({"name": name, "photos": photos})

    def write(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        images_dir = path / "images"
        images_dir.mkdir(exist_ok=True)

        photos_json = []
        for photo in self._photos:
            photo_id = photo["id"]
            images = photo["images"]

            # Create subdirectory for this photo
            photo_dir = images_dir / photo_id
            photo_dir.mkdir(exist_ok=True)

            # Write image files
            image_paths = {}
            front_path = f"images/{photo_id}/front.jpg"
            (path / front_path).write_bytes(images["front"])
            image_paths["front"] = front_path

            if images.get("back"):
                back_path = f"images/{photo_id}/back.jpg"
                (path / back_path).write_bytes(images["back"])
                image_paths["back"] = back_path

            if images.get("enhanced_front"):
                enhanced_path = f"images/{photo_id}/enhanced_front.jpg"
                (path / enhanced_path).write_bytes(images["enhanced_front"])
                image_paths["enhanced_front"] = enhanced_path

            photos_json.append({
                "id": photo_id,
                "images": image_paths,
                "source_filenames": photo["source_filenames"],
            })

        collection_data = {
            "name": self._name,
            "photos": photos_json,
        }

        with open(path / "collection.json", "w") as f:
            json.dump(collection_data, f, indent=2)

