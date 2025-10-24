import cv2
import time
from fer import FER
import numpy as np
from config import Config
from logger import logger
from utils import (
    secure_camera_capture,
    validate_frame,
    sanitize_emotion_label,
    calculate_sleep_probability,
    safe_release_resources
)

class SafeDriveApp:
    """Secure Facial Emotion Recognition application for driver sleep detection."""

    def __init__(self):
        """Initialize the application with secure configuration."""
        try:
            Config.validate_config()
            self.config = Config()
            self.emotion_detector = None
            self.cap = None
            self.frame_count = 0
            self.start_time = time.time()
            logger.info(f"{self.config.APP_NAME} v{self.config.APP_VERSION} initialized")
        except Exception as e:
            logger.error(f"Failed to initialize application: {e}")
            raise

    def initialize_emotion_detector(self):
        """Initialize the emotion detector securely."""
        try:
            self.emotion_detector = FER(mtcnn=True)
            logger.info("Emotion detector initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize emotion detector: {e}")
            raise

    def initialize_camera(self):
        """Initialize camera with security measures."""
        self.cap = secure_camera_capture(
            self.config.CAMERA_INDEX,
            self.config.CAMERA_FALLBACK_INDEX
        )
        if self.cap is None:
            raise RuntimeError("Could not initialize camera")

    def detect_emotion_and_sleep(self, frame: np.ndarray) -> tuple[str, str, float]:
        """
        Detect emotions and determine sleep status with security validations.

        Args:
            frame: Input frame from camera

        Returns:
            Tuple of (emotion, sleep_status, sleep_probability)
        """
        if not validate_frame(frame):
            return "invalid_frame", "Unknown", 0.0

        try:
            # Detect emotions
            emotions = self.emotion_detector.detect_emotions(frame)

            if emotions:
                # Sanitize and get dominant emotion
                dominant_emotion = sanitize_emotion_label(
                    max(emotions[0]['emotions'], key=emotions[0]['emotions'].get)
                )

                # Calculate sleep probability
                sleep_prob = calculate_sleep_probability(emotions[0]['emotions'])

                # Determine sleep status based on probability threshold
                sleep_status = "Possibly Asleep" if sleep_prob > 0.5 else "Awake"

                return dominant_emotion, sleep_status, sleep_prob
            else:
                return "no_face", "Unknown", 0.0

        except Exception as e:
            logger.warning(f"Error in emotion detection: {e}")
            return "error", "Unknown", 0.0

    def process_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Process a frame and add overlay information.

        Args:
            frame: Input frame

        Returns:
            Processed frame with overlays
        """
        # Detect emotion and sleep status
        emotion, sleep_status, sleep_prob = self.detect_emotion_and_sleep(frame)

        # Add text overlays
        cv2.putText(frame, f"Emotion: {emotion}", (10, 30),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Status: {sleep_status}", (10, 70),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Sleep Prob: {sleep_prob:.2f}", (10, 110),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        # Add warning if high sleep probability
        if sleep_prob > 0.7:
            cv2.putText(frame, "WARNING: HIGH SLEEP RISK!", (10, 150),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 3)

        return frame

    def run(self):
        """Main application loop with security measures."""
        try:
            self.initialize_emotion_detector()
            self.initialize_camera()

            logger.info("Starting Facial Emotion Recognition for Driver Sleep Detection...")
            print("Press 'q' to quit safely")

            while True:
                ret, frame = self.cap.read()
                if not ret:
                    logger.warning("Failed to read frame from camera")
                    break

                self.frame_count += 1

                # Skip frames for performance if configured
                if self.frame_count % self.config.FRAME_SKIP != 0:
                    continue

                # Process frame
                processed_frame = self.process_frame(frame)

                # Show the frame
                cv2.imshow('Safe Drive - Driver Sleep Detection', processed_frame)

                # Log performance every 100 frames
                if self.frame_count % 100 == 0:
                    fps = self.frame_count / (time.time() - self.start_time)
                    logger.info(f"Processing at {fps:.2f} FPS")

                # Break loop on 'q' key press
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    logger.info("Application shutdown requested by user")
                    break

        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Unexpected error in main loop: {e}")
        finally:
            self.cleanup()

    def cleanup(self):
        """Secure cleanup of resources."""
        logger.info("Cleaning up resources...")
        safe_release_resources(self.cap)
        cv2.destroyAllWindows()
        logger.info("Application shutdown complete")

def main():
    """Main entry point with error handling."""
    try:
        app = SafeDriveApp()
        app.run()
    except Exception as e:
        logger.critical(f"Critical application error: {e}")
        print(f"Application failed to start: {e}")
        return 1
    return 0

if __name__ == "__main__":
    exit(main())
