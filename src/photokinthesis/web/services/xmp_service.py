"""XMP metadata service for reading and searching photo metadata."""

from pathlib import Path
from typing import Dict, List
from photokinthesis.xmp_parser import parse_xmp_file


class XMPService:
    """Service for reading and searching XMP metadata."""

    def __init__(self, collection_xmp_dir: Path):
        """
        Initialize XMP service.

        Args:
            collection_xmp_dir: Root directory for collection XMP files
        """
        self.collection_xmp_dir = Path(collection_xmp_dir)

    def get_photo_metadata(self, collection_name: str, basename: str) -> Dict:
        """
        Get all metadata for a photo including faces.

        Args:
            collection_name: Name of the collection
            basename: Photo basename (without extension)

        Returns:
            Dictionary with metadata and faces:
            {
                "basename": str,
                "xmp_path": str,
                "metadata": {...},
                "faces": [...]
            }

        Raises:
            FileNotFoundError: If XMP file not found
        """
        xmp_path = self.collection_xmp_dir / collection_name / f"{basename}.xmp"

        if not xmp_path.exists():
            raise FileNotFoundError(f"XMP file not found: {xmp_path}")

        # Parse XMP file
        xmp_data = parse_xmp_file(xmp_path)

        return {
            "basename": basename,
            "xmp_path": str(xmp_path),
            "metadata": xmp_data["metadata"],
            "faces": xmp_data["faces"]
        }

    def search_metadata(self, collection_name: str, query: str) -> List[str]:
        """
        Search for photos with metadata matching query.

        Args:
            collection_name: Name of the collection
            query: Search query string (case-insensitive)

        Returns:
            List of basenames matching the query
        """
        xmp_dir = self.collection_xmp_dir / collection_name
        if not xmp_dir.exists():
            return []

        matching_basenames = []
        query_lower = query.lower()

        # Scan all XMP files
        for xmp_file in xmp_dir.glob("*.xmp"):
            try:
                xmp_data = parse_xmp_file(xmp_file)

                # Search in metadata values
                for value in xmp_data['metadata'].values():
                    if query_lower in str(value).lower():
                        matching_basenames.append(xmp_file.stem)
                        break

                # Also search in face names
                if xmp_file.stem not in matching_basenames:
                    for face in xmp_data['faces']:
                        if query_lower in face.get('name', '').lower():
                            matching_basenames.append(xmp_file.stem)
                            break

            except Exception:
                # Skip files that can't be parsed
                continue

        return matching_basenames

    def get_face_counts(self, collection_name: str, basenames: List[str]) -> Dict[str, int]:
        """
        Get face counts for a list of basenames.

        Args:
            collection_name: Name of the collection
            basenames: List of photo basenames

        Returns:
            Dictionary mapping basename to face count
        """
        xmp_dir = self.collection_xmp_dir / collection_name
        face_counts = {}

        for basename in basenames:
            xmp_path = xmp_dir / f"{basename}.xmp"
            if xmp_path.exists():
                try:
                    xmp_data = parse_xmp_file(xmp_path)
                    face_counts[basename] = len(xmp_data['faces'])
                except Exception:
                    face_counts[basename] = 0
            else:
                face_counts[basename] = 0

        return face_counts
