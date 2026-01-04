"""Facial recognition utilities for photokinthesis."""

from pathlib import Path
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2
import xml.etree.ElementTree as ET
from xml.dom import minidom
import tempfile
import urllib.request
import os
from mtcnn import MTCNN


def recognize_faces(
    collection_xmp_dir: Path,
    collection_name: str,
    collection_image_dir: Path,
) -> None:
    """
    Detect faces in collection images and add face regions to XMP files.

    Args:
        collection_xmp_dir: Root directory for collection XMP files
        collection_name: Name of the collection
        collection_image_dir: Root directory for collection image files
    """
    # Read version from VERSION file
    xmp_dir = collection_xmp_dir / collection_name
    version_file = xmp_dir / "VERSION"

    if not version_file.exists():
        raise ValueError(f"VERSION file not found: {version_file}")

    with open(version_file, "r") as f:
        version = f.read().strip()

    print(f"Processing collection '{collection_name}' version {version}...")

    # Get enhanced_fronts directory for this version
    enhanced_fronts_dir = collection_image_dir / collection_name / version / "enhanced_fronts"

    if not enhanced_fronts_dir.exists():
        raise ValueError(f"Enhanced fronts directory not found: {enhanced_fronts_dir}")

    # Get all XMP files in the collection XMP directory
    xmp_files = sorted(xmp_dir.glob("*.xmp"))
    print(f"Processing {len(xmp_files)} XMP files...")

    for xmp_path in xmp_files:
        # Find corresponding image in enhanced_fronts
        image_name = f"{xmp_path.stem}.jpg"
        img_path = enhanced_fronts_dir / image_name

        if not img_path.exists():
            # Try uppercase extension
            image_name = f"{xmp_path.stem}.JPG"
            img_path = enhanced_fronts_dir / image_name

            if not img_path.exists():
                print(f"Warning: Image not found for {xmp_path.name}, skipping")
                continue

        # Detect faces in the image
        print(f"Detecting faces in {img_path.name}...")
        # Using MTCNN - excellent for old/B&W photos
        face_locations = _detect_faces_mtcnn(img_path)
        # Alternatives:
        # face_locations = _detect_faces_opencv(img_path)  # OpenCV Haar Cascade
        # face_locations = _detect_faces(img_path)  # MediaPipe

        if face_locations:
            print(f"  Found {len(face_locations)} face(s)")
            # Update XMP file with face regions (removes any existing face data first)
            _add_face_regions_to_xmp(xmp_path, face_locations)
        else:
            print(f"  No faces found")
            # Still update XMP to remove any existing face regions
            _add_face_regions_to_xmp(xmp_path, [])

    print(f"Face recognition complete for collection '{collection_name}'!")


def _detect_faces(image_path: Path) -> list:
    """
    Detect faces in an image and return normalized coordinates.

    Args:
        image_path: Path to the image file

    Returns:
        List of face region dictionaries with normalized coordinates
    """
    # Load image with OpenCV
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Warning: Could not load image {image_path}")
        return []

    # Preprocess image for better face detection on old photos
    # Convert to grayscale for histogram equalization
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply histogram equalization to improve contrast
    equalized = cv2.equalizeHist(gray)

    # Convert back to BGR, then to RGB for MediaPipe
    image_enhanced = cv2.cvtColor(equalized, cv2.COLOR_GRAY2BGR)
    image_rgb = cv2.cvtColor(image_enhanced, cv2.COLOR_BGR2RGB)

    # Get image dimensions for normalization
    height, width, _ = image.shape

    # Download model file if needed
    model_path = Path(tempfile.gettempdir()) / "blaze_face_short_range.tflite"
    if not model_path.exists():
        model_url = "https://storage.googleapis.com/mediapipe-models/face_detector/blaze_face_short_range/float16/1/blaze_face_short_range.tflite"
        print(f"Downloading face detection model to {model_path}...")
        urllib.request.urlretrieve(model_url, model_path)

    # Initialize MediaPipe Face Detector with the new API
    base_options = python.BaseOptions(model_asset_path=str(model_path))
    options = vision.FaceDetectorOptions(
        base_options=base_options,
        min_detection_confidence=0.2  # Lowered for better recall on old photos
    )
    detector = vision.FaceDetector.create_from_options(options)

    # Convert to MediaPipe Image format
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=image_rgb)

    # Detect faces
    detection_result = detector.detect(mp_image)

    regions = []
    if detection_result.detections:
        for detection in detection_result.detections:
            # Get bounding box
            bbox = detection.bounding_box

            # Normalize coordinates
            # bbox has: origin_x, origin_y, width, height in pixels
            xmin = bbox.origin_x / width
            ymin = bbox.origin_y / height
            w = bbox.width / width
            h = bbox.height / height

            # Convert to center point (x, y, width, height)
            center_x = xmin + w / 2
            center_y = ymin + h / 2

            region = {
                "x": center_x,
                "y": center_y,
                "w": w,
                "h": h,
            }
            regions.append(region)

    detector.close()
    return regions


def _detect_faces_opencv(image_path: Path) -> list:
    """
    Detect faces using OpenCV Haar Cascade (alternative method, often better for old photos).

    Args:
        image_path: Path to the image file

    Returns:
        List of face region dictionaries with normalized coordinates
    """
    # Load image with OpenCV
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Warning: Could not load image {image_path}")
        return []

    # Get image dimensions
    height, width = image.shape[:2]

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply histogram equalization for better contrast
    gray = cv2.equalizeHist(gray)

    # Load Haar Cascade classifier
    cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
    face_cascade = cv2.CascadeClassifier(cascade_path)

    # Detect faces with multiple scale factors for better recall
    # Try different parameters for better detection on old photos
    faces = face_cascade.detectMultiScale(
        gray,
        scaleFactor=1.05,  # How much image size is reduced at each scale
        minNeighbors=4,   # Lower = more detections but more false positives
        minSize=(15, 15), # Minimum face size
        flags=cv2.CASCADE_SCALE_IMAGE
    )

    regions = []
    for (x, y, w, h) in faces:
        # Normalize coordinates (convert to 0-1 range)
        norm_x = x / width
        norm_y = y / height
        norm_w = w / width
        norm_h = h / height

        # Convert to center point format (MediaPipe format)
        center_x = norm_x + norm_w / 2
        center_y = norm_y + norm_h / 2

        region = {
            "x": center_x,
            "y": center_y,
            "w": norm_w,
            "h": norm_h,
        }
        regions.append(region)

    return regions


def _detect_faces_mtcnn(image_path: Path) -> list:
    """
    Detect faces using MTCNN (Multi-task Cascaded Convolutional Networks).
    Excellent for challenging images including old photos and varying lighting.

    Args:
        image_path: Path to the image file

    Returns:
        List of face region dictionaries with normalized coordinates
    """
    # Load image with OpenCV
    image = cv2.imread(str(image_path))
    if image is None:
        print(f"Warning: Could not load image {image_path}")
        return []

    # Get image dimensions
    height, width = image.shape[:2]

    # Convert BGR to RGB (MTCNN expects RGB)
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

    # Initialize MTCNN detector
    detector = MTCNN()

    # Detect faces
    # Returns list of dicts with 'box' and 'confidence'
    detections = detector.detect_faces(image_rgb)

    regions = []
    for detection in detections:
        # Get bounding box [x, y, width, height]
        box = detection['box']
        confidence = detection['confidence']

        # Skip low confidence detections
        if confidence < 0.80:
            continue

        x, y, w, h = box

        # Ensure box is within image bounds
        x = max(0, x)
        y = max(0, y)
        w = min(w, width - x)
        h = min(h, height - y)

        # Normalize coordinates
        norm_x = x / width
        norm_y = y / height
        norm_w = w / width
        norm_h = h / height

        # Convert to center point format
        center_x = norm_x + norm_w / 2
        center_y = norm_y + norm_h / 2

        region = {
            "x": center_x,
            "y": center_y,
            "w": norm_w,
            "h": norm_h,
        }
        regions.append(region)

    return regions


def _add_face_regions_to_xmp(xmp_path: Path, face_regions: list) -> None:
    """
    Add face region information to an XMP file using Microsoft Photo Region standard.

    Args:
        xmp_path: Path to the XMP file
        face_regions: List of face region dictionaries with normalized coordinates
    """
    # Parse existing XMP file
    tree = ET.parse(xmp_path)
    root = tree.getroot()

    # Define namespaces
    namespaces = {
        "x": "adobe:ns:meta/",
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "mwg-rs": "http://www.metadataworkinggroup.com/schemas/regions/",
        "stArea": "http://ns.adobe.com/xmp/sType/Area#",
    }

    # Register namespaces
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)

    # Find or create RDF element
    rdf = root.find(".//{http://www.w3.org/1999/02/22-rdf-syntax-ns#}RDF")
    if rdf is None:
        raise ValueError("Invalid XMP file: RDF element not found")

    # Find or create Description element for regions
    desc = None
    removed_existing = False
    for description in rdf.findall(
        "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description"
    ):
        # Check if this description already has regions
        existing_regions = description.find(
            "{http://www.metadataworkinggroup.com/schemas/regions/}Regions"
        )
        if existing_regions is not None:
            desc = description
            # Remove existing regions to replace them
            description.remove(existing_regions)
            removed_existing = True
            break

    if desc is None:
        # Create new Description element
        desc = ET.SubElement(
            rdf, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description"
        )
        desc.set("{http://www.w3.org/1999/02/22-rdf-syntax-ns#}about", "")

    # Create Regions structure
    regions_elem = ET.SubElement(
        desc, "{http://www.metadataworkinggroup.com/schemas/regions/}Regions"
    )

    region_list = ET.SubElement(
        regions_elem,
        "{http://www.metadataworkinggroup.com/schemas/regions/}RegionList",
    )

    seq = ET.SubElement(
        region_list, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Seq"
    )

    # Add each face region
    for region in face_regions:
        li = ET.SubElement(seq, "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}li")

        # Add Area
        area = ET.SubElement(
            li, "{http://www.metadataworkinggroup.com/schemas/regions/}Area"
        )

        x_elem = ET.SubElement(area, "{http://ns.adobe.com/xmp/sType/Area#}x")
        x_elem.text = f"{region['x']:.6f}"

        y_elem = ET.SubElement(area, "{http://ns.adobe.com/xmp/sType/Area#}y")
        y_elem.text = f"{region['y']:.6f}"

        w_elem = ET.SubElement(area, "{http://ns.adobe.com/xmp/sType/Area#}w")
        w_elem.text = f"{region['w']:.6f}"

        h_elem = ET.SubElement(area, "{http://ns.adobe.com/xmp/sType/Area#}h")
        h_elem.text = f"{region['h']:.6f}"

        unit_elem = ET.SubElement(area, "{http://ns.adobe.com/xmp/sType/Area#}unit")
        unit_elem.text = "normalized"

        # Add Name
        name_elem = ET.SubElement(
            li, "{http://www.metadataworkinggroup.com/schemas/regions/}Name"
        )
        name_elem.text = "Unknown"

        # Add Type
        type_elem = ET.SubElement(
            li, "{http://www.metadataworkinggroup.com/schemas/regions/}Type"
        )
        type_elem.text = "Face"

    # Write back to file with pretty printing
    xml_str = ET.tostring(root, encoding="unicode")
    dom = minidom.parseString(xml_str)
    pretty_xml = dom.toprettyxml(indent="  ", encoding="UTF-8").decode("utf-8")

    # Remove extra blank lines
    lines = [line for line in pretty_xml.split("\n") if line.strip()]
    formatted_xml = "\n".join(lines)

    with open(xmp_path, "w", encoding="utf-8") as f:
        f.write(formatted_xml)
