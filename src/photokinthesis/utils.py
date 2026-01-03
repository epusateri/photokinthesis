"""Utility functions for photokinthesis."""

from pathlib import Path
from collections import defaultdict
from shutil import copy2
from typing import Dict
import imagehash
from PIL import Image


def reorganize_fast_foto(fast_foto_dir: Path, output_dir: Path) -> None:
    """
    Reorganize files from FastFoto scanning software output.

    Files are organized as follows:
    - basename.jpg -> output_dir/fronts/
    - basename_a.jpg -> output_dir/enhanced_fronts/
    - basename_b.jpg -> output_dir/backs/

    Args:
        fast_foto_dir: Directory containing FastFoto output files
        output_dir: Directory where reorganized files will be written

    Raises:
        ValueError: If output directories exist and are not empty
    """
    # Create output directories
    fronts_dir = output_dir / "fronts"
    enhanced_fronts_dir = output_dir / "enhanced_fronts"
    backs_dir = output_dir / "backs"

    # Verify output directories are empty if they exist
    for dir_path in [fronts_dir, enhanced_fronts_dir, backs_dir]:
        if dir_path.exists() and any(dir_path.iterdir()):
            raise ValueError(
                f"Output directory {dir_path} exists and is not empty. "
                "Please provide an empty output directory."
            )

    # Create the directories
    fronts_dir.mkdir(parents=True, exist_ok=True)
    enhanced_fronts_dir.mkdir(parents=True, exist_ok=True)
    backs_dir.mkdir(parents=True, exist_ok=True)

    # Find all .jpg files recursively
    jpg_files = list(fast_foto_dir.rglob("*.jpg")) + list(fast_foto_dir.rglob("*.JPG"))

    # Group files by their base names, keeping track of directory to handle collisions
    # We use a list of groups to handle cases where the same basename appears in different locations
    file_groups = defaultdict(lambda: defaultdict(dict))

    for jpg_file in jpg_files:
        print(f"Processing {jpg_file}...")
        stem = jpg_file.stem
        parent_dir = jpg_file.parent

        # Determine file type based on suffix pattern
        if stem.endswith("_a"):
            base_name = stem[:-2]  # Remove "_a"
            file_type = "enhanced_front"
        elif stem.endswith("_b"):
            base_name = stem[:-2]  # Remove "_b"
            file_type = "back"
        else:
            base_name = stem
            file_type = "front"

        # Replace spaces with underscores in the basename
        base_name = base_name.replace(" ", "_")

        # Store the file path with its type, grouped by parent directory
        # This ensures files from the same directory stay together
        file_groups[parent_dir][base_name][file_type] = jpg_file

    # Flatten groups and detect basename collisions
    all_groups = []
    for parent_dir, basename_dict in file_groups.items():
        for base_name, files in basename_dict.items():
            all_groups.append((base_name, files))

    # Count how many times each basename appears
    basename_counts = defaultdict(int)
    for base_name, _ in all_groups:
        basename_counts[base_name] += 1

    # Process each file group with collision handling
    counter_per_basename = defaultdict(int)

    for base_name, files in all_groups:
        # Determine unique basename
        if basename_counts[base_name] > 1:
            # This basename has collisions, add a counter
            unique_base_name = f"{base_name}_{counter_per_basename[base_name]}"
            counter_per_basename[base_name] += 1
        else:
            unique_base_name = base_name

        print(f"Copying {base_name}...")
        # Copy front image
        if "front" in files:
            dest_path = fronts_dir / f"{unique_base_name}.jpg"
            copy2(files["front"], dest_path)

        # Copy enhanced front image
        if "enhanced_front" in files:
            dest_path = enhanced_fronts_dir / f"{unique_base_name}.jpg"
            copy2(files["enhanced_front"], dest_path)

        # Copy back image
        if "back" in files:
            dest_path = backs_dir / f"{unique_base_name}.jpg"
            copy2(files["back"], dest_path)


def deduplicate_photos(
    reorganized_dir: Path, output_dir: Path, duplicates_dir: Path, threshold: int = 5
) -> Dict[str, int]:
    """
    Remove duplicate images using perceptual hashing.

    Args:
        reorganized_dir: Directory containing fronts/, enhanced_fronts/, and backs/
        output_dir: Directory where deduplicated files will be written
        duplicates_dir: Directory where duplicate files will be written for review
        threshold: Maximum hash distance to consider images as duplicates (0=exact only)

    Returns:
        Dictionary with statistics about the deduplication process
    """
    # Define input and output directories
    input_fronts = reorganized_dir / "fronts"
    input_enhanced = reorganized_dir / "enhanced_fronts"
    input_backs = reorganized_dir / "backs"

    output_fronts = output_dir / "fronts"
    output_enhanced = output_dir / "enhanced_fronts"
    output_backs = output_dir / "backs"

    # Create output directories
    output_fronts.mkdir(parents=True, exist_ok=True)
    output_enhanced.mkdir(parents=True, exist_ok=True)
    output_backs.mkdir(parents=True, exist_ok=True)
    duplicates_dir.mkdir(parents=True, exist_ok=True)

    # Get all images from fronts directory
    front_images = sorted(input_fronts.glob("*.jpg")) + sorted(input_fronts.glob("*.JPG"))

    print(f"Computing hashes for {len(front_images)} images...")

    # Compute hashes for all images
    image_hashes = {}

    for img_path in front_images:
        try:
            with Image.open(img_path) as img:
                img_hash = imagehash.average_hash(img)
                image_hashes[img_path] = img_hash
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            continue

    print(f"Finding duplicates with threshold {threshold}...")

    # Identify duplicates using hash distance comparison
    kept_files = set()
    duplicate_files = {}  # Maps duplicate file to the original it duplicates
    processed = set()

    # Sort images for consistent ordering
    sorted_images = sorted(image_hashes.keys())

    for i, img1 in enumerate(sorted_images):
        if img1 in processed:
            continue

        # This image will be kept as the original
        kept_files.add(img1)
        processed.add(img1)
        hash1 = image_hashes[img1]

        # Compare with all remaining images
        for img2 in sorted_images[i + 1 :]:
            if img2 in processed:
                continue

            hash2 = image_hashes[img2]
            # Compute Hamming distance between hashes
            distance = hash1 - hash2

            if distance <= threshold:
                # Found a duplicate
                duplicate_files[img2] = img1
                processed.add(img2)
                print(
                    f"Found duplicate: {img2.name} is similar to {img1.name} (distance: {distance})"
                )

    # Copy kept files to output directories
    print(f"\nCopying {len(kept_files)} unique images to output directory...")
    for front_file in kept_files:
        basename = front_file.stem

        # Copy front image
        copy2(front_file, output_fronts / front_file.name)

        # Copy enhanced front if it exists
        enhanced_file = input_enhanced / f"{basename}.jpg"
        if enhanced_file.exists():
            copy2(enhanced_file, output_enhanced / enhanced_file.name)

        # Copy back if it exists
        back_file = input_backs / f"{basename}.jpg"
        if back_file.exists():
            copy2(back_file, output_backs / back_file.name)

    # Copy duplicates to duplicates directory with clear naming
    print(f"\nCopying {len(duplicate_files)} duplicates to duplicates directory...")
    for duplicate_file, original_file in duplicate_files.items():
        dup_basename = duplicate_file.stem
        orig_basename = original_file.stem

        # Copy the kept original
        copy2(original_file, duplicates_dir / f"{orig_basename}_KEPT.jpg")

        # Copy the excluded duplicate with reference to what it duplicates
        # Start with original name so they sort together
        copy2(
            duplicate_file,
            duplicates_dir / f"{orig_basename}_EXCLUDED_{dup_basename}.jpg",
        )

        # Also copy enhanced and back versions if they exist
        dup_enhanced = input_enhanced / f"{dup_basename}.jpg"
        if dup_enhanced.exists():
            copy2(
                dup_enhanced,
                duplicates_dir / f"{orig_basename}_EXCLUDED_{dup_basename}_enhanced.jpg",
            )

        dup_back = input_backs / f"{dup_basename}.jpg"
        if dup_back.exists():
            copy2(
                dup_back,
                duplicates_dir / f"{orig_basename}_EXCLUDED_{dup_basename}_back.jpg",
            )

        orig_enhanced = input_enhanced / f"{orig_basename}.jpg"
        if orig_enhanced.exists():
            copy2(orig_enhanced, duplicates_dir / f"{orig_basename}_KEPT_enhanced.jpg")

        orig_back = input_backs / f"{orig_basename}.jpg"
        if orig_back.exists():
            copy2(orig_back, duplicates_dir / f"{orig_basename}_KEPT_back.jpg")

    return {
        "total": len(front_images),
        "kept": len(kept_files),
        "duplicates": len(duplicate_files),
    }
