import cv2
import numpy as np
from typing import Tuple, Optional
from logger import logger
import dlib
from imutils import face_utils
from scipy.spatial import distance as dist

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

def eye_aspect_ratio(eye):
    """
    Compute the eye aspect ratio (EAR) for a given eye.

    Args:
        eye: Array of eye landmarks

    Returns:
        Eye aspect ratio (float)
    """
    # Vertical eye landmarks
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])

    # Horizontal eye landmark
    C = dist.euclidean(eye[0], eye[3])

    # Eye aspect ratio
    ear = (A + B) / (2.0 * C)

    return ear

def detect_eye_closure(frame: np.ndarray, detector, predictor, ear_thresh: float = 0.25) -> bool:
    """
    Detect if eyes are closed based on eye aspect ratio.

    Args:
        frame: Input frame
        detector: dlib face detector
        predictor: dlib shape predictor
        ear_thresh: Threshold for eye aspect ratio to consider eyes closed

    Returns:
        True if eyes are closed, False otherwise
    """
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    rects = detector(gray, 0)

    if len(rects) == 0:
        return False  # No face detected, assume eyes open

    # Get facial landmarks
    shape = predictor(gray, rects[0])
    shape = face_utils.shape_to_np(shape)

    # Extract left and right eye coordinates
    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    leftEye = shape[lStart:lEnd]
    rightEye = shape[rStart:rEnd]

    # Calculate eye aspect ratios
    leftEAR = eye_aspect_ratio(leftEye)
    rightEAR = eye_aspect_ratio(rightEye)

    # Average the eye aspect ratio
    ear = (leftEAR + rightEAR) / 2.0

    # Return True if eyes are closed (EAR below threshold)
    return ear < ear_thresh

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
