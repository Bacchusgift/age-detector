"""Age estimation module using OpenCV DNN and Caffe model."""

import os
import cv2
import numpy as np

# Age intervals used by the Caffe model
AGE_INTERVALS = [
    "(0-2)", "(4-6)", "(8-12)", "(15-20)",
    "(21-24)", "(25-32)", "(38-43)", "(48-53)", "(60-100)"
]

# Model paths
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models")
AGE_MODEL_PATH = os.path.join(MODEL_DIR, "age_net.caffemodel")
AGE_PROTO_PATH = os.path.join(MODEL_DIR, "age_deploy.prototxt")


class AgeEstimator:
    """Age estimation using Caffe model."""

    def __init__(self):
        """Initialize the age estimator."""
        self.model = None
        self._load_model()

    def _load_model(self):
        """Load the Caffe age estimation model."""
        if not os.path.exists(AGE_MODEL_PATH):
            raise FileNotFoundError(
                f"Age model not found at {AGE_MODEL_PATH}. "
                "Please download age_net.caffemodel and age_deploy.prototxt "
                "and place them in the models/ directory."
            )

        self.model = cv2.dnn.readNetFromCaffe(AGE_PROTO_PATH, AGE_MODEL_PATH)

    def estimate_age(self, face_image: np.ndarray) -> tuple:
        """
        Estimate age from a face image.

        Args:
            face_image: Face image as numpy array (BGR format).

        Returns:
            Tuple of (age_interval, is_under_18, confidence)
        """
        # Preprocess the face image
        blob = cv2.dnn.blobFromImage(
            face_image,
            scalefactor=1.0,
            size=(227, 227),
            mean=(78.4263377603, 87.7689143744, 114.895847746),
            swapRB=False,
            crop=False
        )

        # Pass through the network
        self.model.setInput(blob)
        predictions = self.model.forward()

        # Get the predicted age interval
        max_index = predictions[0].argmax()
        age_interval = AGE_INTERVALS[max_index]
        confidence = float(predictions[0][max_index])

        # Check if under 18
        is_under_18 = self._is_under_18(age_interval)

        return age_interval, is_under_18, confidence

    def _is_under_18(self, age_interval: str) -> bool:
        """
        Determine if the age interval indicates under 18.

        Args:
            age_interval: Age interval string like "(0-2)" or "(15-20)".

        Returns:
            True if the midpoint of the interval is < 18.
        """
        # Parse the interval
        interval = age_interval.strip("()")
        parts = interval.split("-")

        if len(parts) == 2:
            low, high = int(parts[0]), int(parts[1])
            midpoint = (low + high) / 2
            return midpoint < 18

        return False

    def get_age_midpoint(self, age_interval: str) -> float:
        """
        Get the midpoint of an age interval.

        Args:
            age_interval: Age interval string like "(0-2)" or "(15-20)".

        Returns:
            The midpoint of the interval.
        """
        interval = age_interval.strip("()")
        parts = interval.split("-")

        if len(parts) == 2:
            low, high = int(parts[0]), int(parts[1])
            return (low + high) / 2

        return 0.0
