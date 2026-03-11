"""Face detection module using OpenCV DNN."""

import os
import cv2
import numpy as np

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
FACE_MODEL_PATH = os.path.join(MODEL_DIR, "opencv_face_detector_uint8.pb")
FACE_PROTO_PATH = os.path.join(MODEL_DIR, "opencv_face_detector.pbtxt")


class FaceDetector:
    """OpenCV DNN-based face detector."""

    def __init__(self):
        """Initialize the face detector with OpenCV DNN model."""
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the face detection model."""
        # Try to load the OpenCV face detector model
        if os.path.exists(FACE_MODEL_PATH) and os.path.exists(FACE_PROTO_PATH):
            self.model = cv2.dnn.readNetFromTensorflow(FACE_PROTO_PATH, FACE_MODEL_PATH)
            self._use_opencv_dnn = True
        else:
            # Fallback to Haar Cascade (built into OpenCV)
            self.model = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
            self._use_opencv_dnn = False

    def detect_faces(self, image_path: str) -> list:
        """
        Detect faces in an image.

        Args:
            image_path: Path to the input image.

        Returns:
            List of face bounding boxes, each as [x1, y1, x2, y2] coordinates.
        """
        image = cv2.imread(image_path)
        if image is None:
            return []

        return self.detect_faces_from_array(image)

    def detect_faces_from_array(self, image: np.ndarray) -> list:
        """
        Detect faces in a numpy array image.

        Args:
            image: Input image as numpy array (BGR format).

        Returns:
            List of face bounding boxes, each as [x1, y1, x2, y2] coordinates.
        """
        if self._use_opencv_dnn:
            return self._detect_dnn(image)
        else:
            return self._detect_haar(image)

    def _detect_dnn(self, image: np.ndarray) -> list:
        """Detect faces using OpenCV DNN model."""
        h, w = image.shape[:2]

        # Create blob from image
        blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), [104, 117, 123], False, False)

        # Set input and forward pass
        self.model.setInput(blob)
        detections = self.model.forward()

        faces = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]

            # Filter by confidence threshold
            if confidence > 0.5:
                x1 = int(detections[0, 0, i, 3] * w)
                y1 = int(detections[0, 0, i, 4] * h)
                x2 = int(detections[0, 0, i, 5] * w)
                y2 = int(detections[0, 0, i, 6] * h)

                # Ensure coordinates are within image bounds
                x1 = max(0, x1)
                y1 = max(0, y1)
                x2 = min(w, x2)
                y2 = min(h, y2)

                faces.append([x1, y1, x2, y2])

        return faces

    def _detect_haar(self, image: np.ndarray) -> list:
        """Detect faces using Haar Cascade (fallback)."""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        faces_rects = self.model.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        faces = []
        for (x, y, w, h) in faces_rects:
            faces.append([x, y, x + w, y + h])

        return faces
