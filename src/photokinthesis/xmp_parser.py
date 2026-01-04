"""XMP file parsing utilities for photokinthesis."""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, List

# Namespace definitions (shared with collections.py)
NAMESPACES = {
    'x': 'adobe:ns:meta/',
    'rdf': 'http://www.w3.org/1999/02/22-rdf-syntax-ns#',
    'dc': 'http://purl.org/dc/elements/1.1/',
    'xmp': 'http://ns.adobe.com/xap/1.0/',
    'photoshop': 'http://ns.adobe.com/photoshop/1.0/',
    'xmpRights': 'http://ns.adobe.com/xap/1.0/rights/',
    'Iptc4xmpCore': 'http://iptc.org/std/Iptc4xmpCore/1.0/xmlns/',
    'exif': 'http://ns.adobe.com/exif/1.0/',
    'mwg-rs': 'http://www.metadataworkinggroup.com/schemas/regions/',
    'stArea': 'http://ns.adobe.com/xmp/sType/Area#',
}


def parse_xmp_file(xmp_path: Path) -> Dict:
    """
    Parse XMP file and extract metadata and face regions.

    Args:
        xmp_path: Path to the XMP file

    Returns:
        Dictionary with structure:
        {
            "metadata": {
                "dc:source": "...",
                "xmp:CreateDate": "...",
                # ... other tags
            },
            "faces": [
                {
                    "name": "Unknown",
                    "type": "Face",
                    "area": {
                        "x": 0.532909,
                        "y": 0.364185,
                        "w": 0.131635,
                        "h": 0.124748,
                        "unit": "normalized"
                    }
                }
            ]
        }
    """
    if not xmp_path.exists():
        raise FileNotFoundError(f"XMP file not found: {xmp_path}")

    tree = ET.parse(xmp_path)
    root = tree.getroot()

    metadata = {}
    faces = []

    # Find RDF element
    rdf = root.find('.//rdf:RDF', NAMESPACES)
    if rdf is None:
        return {"metadata": metadata, "faces": faces}

    # Find all Description elements
    descriptions = rdf.findall('rdf:Description', NAMESPACES)

    for desc in descriptions:
        # Extract regular metadata tags
        for child in desc:
            tag_name = _extract_tag_name(child.tag)

            # Skip face regions (handled separately)
            if 'Regions' in tag_name:
                faces = _parse_face_regions(child)
                continue

            # Handle text content
            if child.text and child.text.strip():
                metadata[tag_name] = child.text.strip()

    return {
        "metadata": metadata,
        "faces": faces
    }


def _extract_tag_name(tag: str) -> str:
    """
    Extract namespace:name from full XML tag.

    Args:
        tag: Full tag in format {http://namespace/uri}localname

    Returns:
        Tag in format namespace:localname (e.g., "dc:source")
    """
    # Tag format: {http://namespace/uri}localname
    # Convert to: namespace:localname
    for prefix, uri in NAMESPACES.items():
        if tag.startswith(f'{{{uri}}}'):
            local_name = tag[len(f'{{{uri}}}'):]
            return f'{prefix}:{local_name}'

    # If no namespace match, return as-is (strip braces if present)
    if tag.startswith('{'):
        # Unknown namespace, just return local name
        return tag.split('}')[1] if '}' in tag else tag
    return tag


def _parse_face_regions(regions_elem) -> List[Dict]:
    """
    Parse mwg-rs:Regions element to extract face information.

    Args:
        regions_elem: The mwg-rs:Regions XML element

    Returns:
        List of face dictionaries with structure:
        [
            {
                "name": "Unknown",
                "type": "Face",
                "area": {
                    "x": 0.532909,
                    "y": 0.364185,
                    "w": 0.131635,
                    "h": 0.124748,
                    "unit": "normalized"
                }
            }
        ]
    """
    faces = []

    # Navigate: Regions -> RegionList -> Seq -> li elements
    region_list = regions_elem.find('mwg-rs:RegionList', NAMESPACES)
    if region_list is None:
        return faces

    seq = region_list.find('rdf:Seq', NAMESPACES)
    if seq is None:
        return faces

    li_elements = seq.findall('rdf:li', NAMESPACES)

    for li in li_elements:
        face = {}

        # Extract Area coordinates
        area_elem = li.find('mwg-rs:Area', NAMESPACES)
        if area_elem is not None:
            try:
                face['area'] = {
                    'x': float(area_elem.findtext('stArea:x', '0', NAMESPACES)),
                    'y': float(area_elem.findtext('stArea:y', '0', NAMESPACES)),
                    'w': float(area_elem.findtext('stArea:w', '0', NAMESPACES)),
                    'h': float(area_elem.findtext('stArea:h', '0', NAMESPACES)),
                    'unit': area_elem.findtext('stArea:unit', 'normalized', NAMESPACES),
                }
            except (ValueError, TypeError):
                # Skip faces with invalid coordinates
                continue
        else:
            # Skip faces without area
            continue

        # Extract Name
        name_elem = li.find('mwg-rs:Name', NAMESPACES)
        if name_elem is not None and name_elem.text:
            face['name'] = name_elem.text
        else:
            face['name'] = 'Unknown'

        # Extract Type
        type_elem = li.find('mwg-rs:Type', NAMESPACES)
        if type_elem is not None and type_elem.text:
            face['type'] = type_elem.text
        else:
            face['type'] = 'Face'

        faces.append(face)

    return faces
