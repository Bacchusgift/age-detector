"""HTTP API server for age checker - for n8n integration."""

import base64
import io
import tempfile
import os

import cv2
import numpy as np
from flask import Flask, request, jsonify
from PIL import Image

from .detector import FaceDetector
from .age_estimator import AgeEstimator

app = Flask(__name__)

# Initialize detector and estimator (loaded once at startup)
detector = None
estimator = None


def get_detector():
    global detector
    if detector is None:
        detector = FaceDetector()
    return detector


def get_estimator():
    global estimator
    if estimator is None:
        estimator = AgeEstimator()
    return estimator


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint."""
    return jsonify({"status": "ok", "service": "age-checker"})


@app.route('/check', methods=['POST'])
def check_image():
    """
    Check an image for underage people.

    Expects JSON body with:
    - image: base64 encoded image data
    - or url: URL to fetch image from (optional, not implemented)

    Returns JSON with detection results.
    """
    try:
        data = request.get_json()

        if not data or 'image' not in data:
            return jsonify({
                "error": "Missing 'image' field with base64 encoded image"
            }), 400

        # Decode base64 image
        image_data = data['image']

        # Handle data URL format (data:image/jpeg;base64,...)
        if image_data.startswith('data:'):
            image_data = image_data.split(',', 1)[1]

        image_bytes = base64.b64decode(image_data)

        # Convert to numpy array
        pil_image = Image.open(io.BytesIO(image_bytes))
        pil_image = pil_image.convert('RGB')
        image = np.array(pil_image)
        # Convert RGB to BGR (OpenCV format)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

        # Detect faces
        faces = get_detector().detect_faces_from_array(image)

        results = []
        underage_count = 0

        for i, (x1, y1, x2, y2) in enumerate(faces):
            # Extract face region
            face = image[y1:y2, x1:x2]

            if face.size == 0:
                continue

            try:
                age_interval, is_under_18, confidence = get_estimator().estimate_age(face)
                age_midpoint = get_estimator().get_age_midpoint(age_interval)

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

        return jsonify({
            "success": True,
            "faces_detected": len(faces),
            "underage_count": underage_count,
            "results": results
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/check/file', methods=['POST'])
def check_file():
    """
    Check an uploaded file for underage people.

    Expects multipart/form-data with 'file' field.
    Returns JSON with detection results.
    """
    try:
        if 'file' not in request.files:
            return jsonify({
                "error": "No file uploaded"
            }), 400

        file = request.files['file']

        # Read image
        image_bytes = file.read()
        nparr = np.frombuffer(image_bytes, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)

        if image is None:
            return jsonify({
                "error": "Could not read image file"
            }), 400

        # Detect faces
        faces = get_detector().detect_faces_from_array(image)

        results = []
        underage_count = 0

        for i, (x1, y1, x2, y2) in enumerate(faces):
            face = image[y1:y2, x1:x2]

            if face.size == 0:
                continue

            try:
                age_interval, is_under_18, confidence = get_estimator().estimate_age(face)
                age_midpoint = get_estimator().get_age_midpoint(age_interval)

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

        return jsonify({
            "success": True,
            "filename": file.filename,
            "faces_detected": len(faces),
            "underage_count": underage_count,
            "results": results
        })

    except Exception as e:
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


def main():
    """Run the API server."""
    import argparse

    parser = argparse.ArgumentParser(description='Age Checker API Server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=5000, help='Port to bind to')
    parser.add_argument('--debug', action='store_true', help='Enable debug mode')

    args = parser.parse_args()

    print(f"Starting Age Checker API server on {args.host}:{args.port}")
    print(f"Endpoints:")
    print(f"  GET  /health - Health check")
    print(f"  POST /check  - Check image (JSON body with base64 image)")
    print(f"  POST /check/file - Check uploaded file (multipart form)")

    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == '__main__':
    main()
