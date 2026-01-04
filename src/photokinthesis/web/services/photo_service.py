"""Photo service for listing and serving images."""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from PIL import Image, ImageOps
from io import BytesIO


# Thumbnail size configurations
THUMBNAIL_SIZES = {
    'thumb': (300, 300),
    'medium': (800, 800),
    'full': None  # Original size
}


@dataclass
class PhotoInfo:
    """Information about a photo."""
    filename: str
    basename: str
    thumbnail_url: str
    full_url: str
    has_xmp: bool
    has_faces: bool = False
    face_count: int = 0

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class PhotoService:
    """Service for listing and serving photo files."""

    def __init__(self, collection_xmp_dir: Path, collection_image_dir: Path):
        """
        Initialize photo service.

        Args:
            collection_xmp_dir: Root directory for collection XMP files
            collection_image_dir: Root directory for collection image files
        """
        self.collection_xmp_dir = Path(collection_xmp_dir)
        self.collection_image_dir = Path(collection_image_dir)

    def list_photos(
        self,
        collection_name: str,
        offset: int = 0,
        limit: int = 50,
        search_basenames: Optional[List[str]] = None
    ) -> Dict:
        """
        List photos in a collection with pagination.

        Args:
            collection_name: Name of the collection
            offset: Pagination offset
            limit: Number of photos to return
            search_basenames: Optional list of basenames to filter by (from search)

        Returns:
            Dictionary with photos list and pagination info:
            {
                "photos": [PhotoInfo, ...],
                "total": int,
                "offset": int,
                "limit": int
            }
        """
        # Get collection info for version
        xmp_dir = self.collection_xmp_dir / collection_name
        if not xmp_dir.exists():
            raise ValueError(f"Collection not found: {collection_name}")

        version_file = xmp_dir / "VERSION"
        if not version_file.exists():
            raise ValueError(f"VERSION file not found: {version_file}")

        with open(version_file, 'r') as f:
            version = f.read().strip()

        # Find enhanced_fronts directory
        enhanced_fronts_dir = self.collection_image_dir / collection_name / version / "enhanced_fronts"
        if not enhanced_fronts_dir.exists():
            raise ValueError(f"Enhanced fronts directory not found: {enhanced_fronts_dir}")

        # Get all image files
        image_files = sorted(enhanced_fronts_dir.glob("*.jpg")) + sorted(enhanced_fronts_dir.glob("*.JPG"))

        # Filter by search basenames if provided
        if search_basenames is not None:
            search_set = set(search_basenames)
            image_files = [f for f in image_files if f.stem in search_set]

        total = len(image_files)

        # Apply pagination
        paginated_files = image_files[offset:offset + limit]

        # Build photo info list
        photos = []
        for img_path in paginated_files:
            basename = img_path.stem
            filename = img_path.name

            # Check if XMP file exists
            xmp_path = xmp_dir / f"{basename}.xmp"
            has_xmp = xmp_path.exists()

            # Build URLs
            thumbnail_url = f"/api/images/{collection_name}/{version}/enhanced_fronts/{filename}?size=thumb"
            full_url = f"/api/images/{collection_name}/{version}/enhanced_fronts/{filename}"

            photo = PhotoInfo(
                filename=filename,
                basename=basename,
                thumbnail_url=thumbnail_url,
                full_url=full_url,
                has_xmp=has_xmp
            )
            photos.append(photo)

        return {
            "photos": [p.to_dict() for p in photos],
            "total": total,
            "offset": offset,
            "limit": limit
        }

    def get_image_path(
        self,
        collection_name: str,
        version: str,
        photo_type: str,
        filename: str
    ) -> Path:
        """
        Get absolute path to an image file with security validation.

        Args:
            collection_name: Name of the collection
            version: Collection version
            photo_type: Type of photo ("enhanced_fronts", "fronts", "backs")
            filename: Image filename

        Returns:
            Validated Path object

        Raises:
            ValueError: If path is invalid or outside allowed directory
            FileNotFoundError: If file doesn't exist
        """
        # Validate photo_type
        if photo_type not in ['enhanced_fronts', 'fronts', 'backs']:
            raise ValueError(f"Invalid photo type: {photo_type}")

        # Construct and validate path
        image_path = validate_path(
            self.collection_image_dir,
            collection_name,
            version,
            photo_type,
            filename
        )

        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        return image_path

    def serve_image(self, image_path: Path, size: str = 'full') -> bytes:
        """
        Load and optionally resize an image.

        Args:
            image_path: Path to the image file
            size: Size variant ("thumb", "medium", "full")

        Returns:
            Image data as bytes (JPEG format)
        """
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        # Load image and apply EXIF orientation
        img = Image.open(image_path)

        # Apply EXIF orientation (fixes rotated images from Preview, etc.)
        img = ImageOps.exif_transpose(img)

        # Convert to RGB if necessary (for JPEG compatibility)
        if img.mode in ('RGBA', 'LA', 'P'):
            img = img.convert('RGB')

        # For full size, return with orientation corrected
        if size == 'full':
            buffer = BytesIO()
            img.save(buffer, format='JPEG', quality=95)
            return buffer.getvalue()

        # Resize maintaining aspect ratio
        target_size = THUMBNAIL_SIZES.get(size, THUMBNAIL_SIZES['thumb'])
        img.thumbnail(target_size, Image.Resampling.LANCZOS)

        # Save to bytes buffer
        buffer = BytesIO()
        img.save(buffer, format='JPEG', quality=85)
        return buffer.getvalue()


def validate_path(base_dir: Path, *parts: str) -> Path:
    """
    Validate that constructed path is within base directory.
    Prevents directory traversal attacks.

    Args:
        base_dir: Base directory that all paths must be within
        *parts: Path components to join

    Returns:
        Validated absolute Path object

    Raises:
        ValueError: If resolved path is outside base directory
    """
    # Construct path
    path = base_dir / Path(*parts)

    # Resolve to absolute path
    resolved = path.resolve()
    base_resolved = base_dir.resolve()

    # Ensure it's within base directory
    try:
        resolved.relative_to(base_resolved)
    except ValueError:
        raise ValueError(f"Invalid path: path escapes base directory")

    return resolved
