from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO

from PIL import Image


class Photo:
    """Represents a photo in the collection."""

    THUMBNAIL_SIZE = (200, 200)

    @dataclass
    class Images:
        front: bytes
        back: bytes | None
        enhanced_front: bytes | None
        thumbnail: bytes | None = None
        # Orientation values: 0, 90, 180, 270 (degrees clockwise)
        front_orientation: int = 0
        back_orientation: int = 0
        enhanced_front_orientation: int = 0

    def __init__(self, data: dict) -> None:
        self._id = data["id"]
        self._images = Photo.Images(
            front=data["images"]["front"],
            back=data["images"].get("back"),
            enhanced_front=data["images"].get("enhanced_front"),
            thumbnail=data["images"].get("thumbnail"),
            front_orientation=data["images"].get("front_orientation", 0),
            back_orientation=data["images"].get("back_orientation", 0),
            enhanced_front_orientation=data["images"].get("enhanced_front_orientation", 0),
        )
        self._source_filenames = data["source_filenames"]

    @property
    def id(self) -> str:
        return self._id

    @property
    def images(self) -> Images:
        return self._images

    @property
    def source_filenames(self) -> list[str]:
        return self._source_filenames

    def add_thumbnail(self) -> None:
        """Generate a thumbnail from the front image.

        Note: Images are expected to be normalized (EXIF orientation already
        applied to pixels) before this is called.
        """
        # Use enhanced_front if available, otherwise front
        source = self._images.enhanced_front or self._images.front

        img = Image.open(BytesIO(source))
        img.thumbnail(self.THUMBNAIL_SIZE)

        buffer = BytesIO()
        img.save(buffer, format="JPEG")
        self._images.thumbnail = buffer.getvalue()

    def set_orientation(self, image_type: str, orientation: int) -> None:
        """Set the orientation for a specific image type.

        Args:
            image_type: One of 'front', 'back', 'enhanced_front'
            orientation: Rotation in degrees (0, 90, 180, 270)
        """
        if orientation not in (0, 90, 180, 270):
            raise ValueError(f"Invalid orientation: {orientation}")

        if image_type == "front":
            self._images.front_orientation = orientation
        elif image_type == "back":
            self._images.back_orientation = orientation
        elif image_type == "enhanced_front":
            self._images.enhanced_front_orientation = orientation
        else:
            raise ValueError(f"Invalid image type: {image_type}")

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "id": self._id,
            "images": {
                "front": self._images.front,
                "back": self._images.back,
                "enhanced_front": self._images.enhanced_front,
                "thumbnail": self._images.thumbnail,
                "front_orientation": self._images.front_orientation,
                "back_orientation": self._images.back_orientation,
                "enhanced_front_orientation": self._images.enhanced_front_orientation,
            },
            "source_filenames": self._source_filenames,
        }
        
    
