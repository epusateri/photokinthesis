from dataclasses import dataclass


class Photo:
    """Represents a photo in the collection."""

    @dataclass
    class Images:
        front: bytes
        back: bytes | None
        enhanced_front: bytes | None

    def _load_images(self, images_dict: dict) -> "Photo.Images":
        return Photo.Images(
            front=images_dict["front"],
            back=images_dict.get("back"),
            enhanced_front=images_dict.get("enhanced_front"),
        )
        
    def __init__(self, data: dict) -> None:
        self._id = data["id"]
        self._images = self._load_images(data["images"])
        self._source_filenames = data["source_filenames"]
        
    
