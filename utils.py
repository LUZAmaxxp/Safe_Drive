import cv2
import numpy as np
from typing import Tuple, Optional
from logger import logger

def secure_camera_capture(camera_index: int = 0, fallback_index: int = 1) -> Optional[cv2.VideoCapture]:
    """
    Securely initialize camera capture with fallback options.

    Args:
        camera_index: Primary camera index
        fallback_index: Fallback camera index

    Returns:
        VideoCapture object or None if failed
    """
    for index in [camera_index, fallback_index]:
        try:
            cap = cv2.VideoCapture(index, cv2.CAP_DSHOW)  # Use DirectShow on Windows for better compatibility
            if cap.isOpened():
                logger.info(f"Camera initialized successfully on index {index}")
                return cap
            else:
                cap.release()
        except Exception as e:
            logger.warning(f"Failed to initialize camera on index {index}: {e}")

    logger.error("Failed to initialize any camera")
    return None

def validate_frame(frame: np.ndarray) -> bool:
    """
    Validate that a frame is properly captured and not corrupted.

    Args:
        frame: Captured frame

    Returns:
        True if frame is valid, False otherwise
    """
    if frame is None:
        return False

    if len(frame.shape) != 3 or frame.shape[2] != 3:
        logger.warning("Invalid frame shape")
        return False

    if frame.size == 0:
        logger.warning("Empty frame captured")
        return False

    return True

def sanitize_emotion_label(emotion: str) -> str:
    """
    Sanitize emotion label to prevent injection or unexpected values.

    Args:
        emotion: Raw emotion string

    Returns:
        Sanitized emotion string
    """
    allowed_emotions = ['angry', 'disgust', 'fear', 'happy', 'sad', 'surprise', 'neutral']
    emotion = emotion.lower().strip()

    if emotion in allowed_emotions:
        return emotion
    else:
        logger.warning(f"Unknown emotion detected: {emotion}")
        return 'unknown'

def calculate_sleep_probability(emotions: dict) -> float:
    """
    Calculate sleep probability based on emotion scores.

    Args:
        emotions: Dictionary of emotion scores

    Returns:
        Probability of being asleep (0.0 to 1.0)
    """
    # Weights for sleep-indicating emotions
    sleep_weights = {
        'sad': 0.4,
        'neutral': 0.3,
        'fear': 0.2,
        'angry': 0.1
    }

    total_weight = 0.0
    weighted_sum = 0.0

    for emotion, score in emotions.items():
        if emotion in sleep_weights:
            weighted_sum += score * sleep_weights[emotion]
            total_weight += sleep_weights[emotion]

    if total_weight == 0:
        return 0.0

    return min(weighted_sum / total_weight, 1.0)

def safe_release_resources(*resources):
    """
    Safely release resources like camera captures.

    Args:
        *resources: Resources to release
    """
    for resource in resources:
        try:
            if hasattr(resource, 'release'):
                resource.release()
            elif hasattr(resource, 'close'):
                resource.close()
        except Exception as e:
            logger.warning(f"Error releasing resource: {e}")
