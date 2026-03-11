"""Command-line interface for age checker."""

import argparse
import json
import os
import sys
from pathlib import Path

import cv2
import numpy as np

from .detector import FaceDetector
from .age_estimator import AgeEstimator


def check_image(image_path: str, detector: FaceDetector, estimator: AgeEstimator) -> dict:
    """
    Check a single image for underage people.

    Args:
        image_path: Path to the image file.
        detector: FaceDetector instance.
        estimator: AgeEstimator instance.

    Returns:
        Dictionary with detection results.
    """
    # Read the image
    image = cv2.imread(image_path)
    if image is None:
        return {
            "image": image_path,
            "error": "Could not read image file"
        }

    # Detect faces
    faces = detector.detect_faces_from_array(image)

    if not faces:
        return {
            "image": image_path,
            "faces_detected": 0,
            "underage_count": 0,
            "results": []
        }

    results = []
    underage_count = 0

    for i, (x1, y1, x2, y2) in enumerate(faces):
        # Extract face region
        face = image[y1:y2, x1:x2]

        if face.size == 0:
            continue

        # Estimate age
        try:
            age_interval, is_under_18, confidence = estimator.estimate_age(face)
            age_midpoint = estimator.get_age_midpoint(age_interval)

            result = {
                "face_id": i + 1,
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                "age_interval": age_interval,
                "estimated_age": float(age_midpoint),
                "is_under_18": bool(is_under_18),
                "confidence": round(float(confidence), 4)
            }

            if is_under_18:
                underage_count += 1

            results.append(result)
        except Exception as e:
            results.append({
                "face_id": i + 1,
                "bbox": [int(x1), int(y1), int(x2), int(y2)],
                "error": str(e)
            })

    return {
        "image": image_path,
        "faces_detected": len(faces),
        "underage_count": underage_count,
        "results": results
    }


def visualize_results(image_path: str, results: dict, output_path: str = None):
    """
    Draw visualization on the image.

    Args:
        image_path: Path to the original image.
        results: Detection results dictionary.
        output_path: Optional path to save the visualization.
    """
    image = cv2.imread(image_path)

    for result in results.get("results", []):
        if "bbox" not in result:
            continue

        x1, y1, x2, y2 = result["bbox"]

        # Choose color based on underage status
        color = (0, 0, 255) if result.get("is_under_18", False) else (0, 255, 0)

        # Draw bounding box
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)

        # Prepare label
        if "error" in result:
            label = f"Error: {result['error']}"
        else:
            label = f"{result['age_interval']} {'(UNDERAGE)' if result['is_under_18'] else ''}"

        # Draw label background
        (label_w, label_h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(image, (x1, y1 - label_h - 10), (x1 + label_w, y1), color, -1)

        # Draw label text
        cv2.putText(
            image, label, (x1, y1 - 5),
            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1
        )

    # Show or save the image
    if output_path:
        cv2.imwrite(output_path, image)
        print(f"Visualization saved to: {output_path}")
    else:
        cv2.imshow("Age Detection Result", image)
        cv2.waitKey(0)
        cv2.destroyAllWindows()


def process_path(path: str, output: str = None, visualize: bool = False):
    """
    Process an image or directory of images.

    Args:
        path: Path to image file or directory.
        output: Optional path for JSON output.
        visualize: Whether to show visualization.
    """
    # Initialize detector and estimator
    try:
        detector = FaceDetector()
        estimator = AgeEstimator()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)

    # Collect image paths
    path_obj = Path(path)
    if path_obj.is_file():
        image_paths = [str(path_obj)]
    elif path_obj.is_dir():
        # Support common image formats
        image_paths = []
        for ext in ["*.jpg", "*.jpeg", "*.png", "*.bmp", "*.webp"]:
            image_paths.extend(path_obj.glob(ext))
        image_paths = [str(p) for p in image_paths]
    else:
        print(f"Error: {path} is not a valid file or directory")
        sys.exit(1)

    if not image_paths:
        print("No images found")
        sys.exit(0)

    # Process each image
    all_results = []
    for image_path in image_paths:
        print(f"Processing: {image_path}")
        result = check_image(image_path, detector, estimator)
        all_results.append(result)

        # Print summary
        if "error" in result:
            print(f"  Error: {result['error']}")
        else:
            print(f"  Faces: {result['faces_detected']}, Underage: {result['underage_count']}")

        # Visualize if requested
        if visualize:
            vis_output = None
            if output:
                output_dir = Path(output).parent
                vis_name = f"vis_{Path(image_path).stem}.jpg"
                vis_output = str(output_dir / vis_name)
            visualize_results(image_path, result, vis_output)

    # Output results
    output_data = {
        "summary": {
            "total_images": len(all_results),
            "total_faces": sum(r.get("faces_detected", 0) for r in all_results),
            "total_underage": sum(r.get("underage_count", 0) for r in all_results)
        },
        "results": all_results
    }

    if output:
        with open(output, "w") as f:
            json.dump(output_data, f, indent=2)
        print(f"\nResults saved to: {output}")
    else:
        print("\n" + json.dumps(output_data, indent=2))


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description="Detect if people in images are underage (under 18)"
    )
    subparsers = parser.add_subparsers(dest="command", help="Commands")

    # Check command
    check_parser = subparsers.add_parser("check", help="Check images for underage people")
    check_parser.add_argument(
        "path",
        help="Path to image file or directory"
    )
    check_parser.add_argument(
        "--output", "-o",
        help="Path to save JSON results"
    )
    check_parser.add_argument(
        "--visualize", "-v",
        action="store_true",
        help="Show/save visualization of results"
    )

    args = parser.parse_args()

    if args.command == "check":
        process_path(args.path, args.output, args.visualize)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
