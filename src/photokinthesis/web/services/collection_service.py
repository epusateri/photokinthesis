"""Collection service for discovering and managing photo collections."""

from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict


@dataclass
class CollectionInfo:
    """Information about a photo collection."""
    name: str
    version: str
    photo_count: int
    xmp_path: str
    image_path: str

    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return asdict(self)


class CollectionService:
    """Service for discovering and retrieving collection information."""

    def __init__(self, collection_xmp_dir: Path, collection_image_dir: Path):
        """
        Initialize collection service.

        Args:
            collection_xmp_dir: Root directory for collection XMP files
            collection_image_dir: Root directory for collection image files
        """
        self.collection_xmp_dir = Path(collection_xmp_dir)
        self.collection_image_dir = Path(collection_image_dir)

    def list_collections(self) -> List[CollectionInfo]:
        """
        Discover all collections by scanning XMP directory.

        Returns:
            List of CollectionInfo objects for all discovered collections
        """
        collections = []

        if not self.collection_xmp_dir.exists():
            return collections

        # Scan for subdirectories in XMP directory
        for collection_dir in self.collection_xmp_dir.iterdir():
            if not collection_dir.is_dir():
                continue

            try:
                collection_info = self.get_collection_info(collection_dir.name)
                if collection_info:
                    collections.append(collection_info)
            except (ValueError, FileNotFoundError):
                # Skip collections that don't have required files
                continue

        return sorted(collections, key=lambda c: c.name)

    def get_collection_info(self, collection_name: str) -> Optional[CollectionInfo]:
        """
        Get detailed info about a specific collection.

        Args:
            collection_name: Name of the collection

        Returns:
            CollectionInfo object or None if collection not found

        Raises:
            ValueError: If VERSION file not found or invalid
        """
        xmp_dir = self.collection_xmp_dir / collection_name
        if not xmp_dir.exists():
            return None

        # Read VERSION file
        version_file = xmp_dir / "VERSION"
        if not version_file.exists():
            raise ValueError(f"VERSION file not found: {version_file}")

        with open(version_file, 'r') as f:
            version = f.read().strip()

        # Count XMP files (excluding VERSION file)
        xmp_files = list(xmp_dir.glob("*.xmp"))
        photo_count = len(xmp_files)

        # Construct image path
        image_path = self.collection_image_dir / collection_name / version

        return CollectionInfo(
            name=collection_name,
            version=version,
            photo_count=photo_count,
            xmp_path=str(xmp_dir),
            image_path=str(image_path)
        )
