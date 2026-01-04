"""Collection management utilities for photokinthesis."""

from pathlib import Path
from shutil import copytree
from typing import Dict
import xml.etree.ElementTree as ET
from xml.dom import minidom


def init_collection(
    reorganized_dir: Path,
    collection_name: str,
    collection_xmp_dir: Path,
    collection_image_dir: Path,
    tags: Dict[str, str],
) -> None:
    """
    Initialize a new photo collection with XMP metadata.

    Args:
        reorganized_dir: Directory containing fronts/, enhanced_fronts/, and backs/
        collection_name: Name of the collection
        collection_xmp_dir: Root directory for collection XMP files
        collection_image_dir: Root directory for collection image files
        tags: Dictionary of XMP tag/value pairs (e.g., {"dc:creator": "John Doe"})
    """
    version = "0000"

    # Create collection directories
    image_dest = collection_image_dir / collection_name / version
    xmp_dest = collection_xmp_dir / collection_name

    print(f"Creating collection '{collection_name}' version {version}...")

    # Copy image files from reorganized directory
    print(f"Copying images from {reorganized_dir} to {image_dest}...")
    copytree(reorganized_dir, image_dest, dirs_exist_ok=True)

    # Create XMP directory
    xmp_dest.mkdir(parents=True, exist_ok=True)

    # Get all enhanced front images
    enhanced_fronts_dir = image_dest / "enhanced_fronts"
    if not enhanced_fronts_dir.exists():
        raise ValueError(f"Enhanced fronts directory not found: {enhanced_fronts_dir}")

    enhanced_images = sorted(enhanced_fronts_dir.glob("*.jpg")) + sorted(
        enhanced_fronts_dir.glob("*.JPG")
    )

    print(f"Creating XMP files for {len(enhanced_images)} images...")

    # Create XMP file for each enhanced front image
    for img_path in enhanced_images:
        xmp_filename = f"{img_path.stem}.xmp"
        xmp_path = xmp_dest / xmp_filename

        # Generate XMP content
        xmp_content = _generate_xmp(tags)

        # Write XMP file
        with open(xmp_path, "w", encoding="utf-8") as f:
            f.write(xmp_content)

    # Create VERSION file
    version_file = xmp_dest / "VERSION"
    with open(version_file, "w", encoding="utf-8") as f:
        f.write(version)

    print(f"Collection '{collection_name}' initialized successfully!")
    print(f"  Images: {image_dest}")
    print(f"  XMP files: {xmp_dest}")
    print(f"  Version: {version}")


def _generate_xmp(tags: Dict[str, str]) -> str:
    """
    Generate XMP content from tag/value pairs.

    Args:
        tags: Dictionary of XMP tag/value pairs (e.g., {"dc:creator": "John Doe"})

    Returns:
        XMP XML string
    """
    # Define namespace mappings
    namespace_map = {
        "dc": "http://purl.org/dc/elements/1.1/",
        "xmp": "http://ns.adobe.com/xap/1.0/",
        "photoshop": "http://ns.adobe.com/photoshop/1.0/",
        "xmpRights": "http://ns.adobe.com/xap/1.0/rights/",
        "Iptc4xmpCore": "http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/",
        "exif": "http://ns.adobe.com/exif/1.0/",
    }

    # Register namespaces with ElementTree
    for prefix, uri in namespace_map.items():
        ET.register_namespace(prefix, uri)

    # Also register required namespaces
    ET.register_namespace("x", "adobe:ns:meta/")
    ET.register_namespace("rdf", "http://www.w3.org/1999/02/22-rdf-syntax-ns#")

    # Create root element
    xmpmeta = ET.Element("{adobe:ns:meta/}xmpmeta")
    xmpmeta.set("{adobe:ns:meta/}xmptk", "Python XMP Toolkit")

    # Create RDF element
    rdf = ET.SubElement(xmpmeta, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF")

    # Group tags by namespace
    tags_by_namespace = {}
    for tag_name, tag_value in tags.items():
        if ":" in tag_name:
            namespace_prefix, local_name = tag_name.split(":", 1)
            if namespace_prefix not in namespace_map:
                # Use a custom namespace for unknown prefixes
                namespace_uri = f"http://ns.example.com/{namespace_prefix}/1.0/"
                namespace_map[namespace_prefix] = namespace_uri
                ET.register_namespace(namespace_prefix, namespace_uri)
                print(
                    f"Warning: Unknown namespace prefix '{namespace_prefix}', using custom namespace"
                )
            else:
                namespace_uri = namespace_map[namespace_prefix]

            if namespace_uri not in tags_by_namespace:
                tags_by_namespace[namespace_uri] = []
            tags_by_namespace[namespace_uri].append((local_name, tag_value))
        else:
            # Default to Dublin Core if no prefix specified
            dc_uri = namespace_map["dc"]
            if dc_uri not in tags_by_namespace:
                tags_by_namespace[dc_uri] = []
            tags_by_namespace[dc_uri].append((tag_name, tag_value))

    # Create Description element for each namespace
    for namespace_uri, tag_list in tags_by_namespace.items():
        description = ET.SubElement(
            rdf,
            "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description",
        )
        description.set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")

        # Add tags to this description
        for local_name, value in tag_list:
            tag_elem = ET.SubElement(description, f"{{{namespace_uri}}}{local_name}")
            tag_elem.text = value

    # Convert to string with pretty printing
    xml_str = ET.tostring(xmpmeta, encoding="unicode")

    # Add XML declaration and format nicely
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")

    # Remove extra blank lines
    lines = [line for line in pretty_xml.split("\n") if line.strip()]
    return "\n".join(lines)
