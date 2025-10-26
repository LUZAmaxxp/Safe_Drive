import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Configuration class for the Safe Drive application."""

    # Application Settings
    APP_NAME = os.getenv('APP_NAME', 'Safe_Drive')
    APP_VERSION = os.getenv('APP_VERSION', '1.0.0')
    DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'

    # Security Settings
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key-change-in-production')
    ALLOWED_HOSTS = os.getenv('ALLOWED_HOSTS', 'localhost,127.0.0.1').split(',')

    # Webcam Settings
    CAMERA_INDEX = int(os.getenv('CAMERA_INDEX', 0))
    CAMERA_FALLBACK_INDEX = int(os.getenv('CAMERA_FALLBACK_INDEX', 1))

    # Model Settings
    MODEL_PATH = os.getenv('MODEL_PATH', 'models/emotion_model_trained.h5')
    DATA_PATH = os.getenv('DATA_PATH', 'data/fer2013.csv')
    SHAPE_PREDICTOR_PATH = os.getenv('SHAPE_PREDICTOR_PATH', 'models/shape_predictor_68_face_landmarks.dat')

    # Logging Settings
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE = os.getenv('LOG_FILE', 'logs/app.log')
    URL_DLIB = os.getenv('Dlib_URL', 'https://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2')

    # Performance Settings
    MAX_FPS = int(os.getenv('MAX_FPS', 30))
    FRAME_SKIP = int(os.getenv('FRAME_SKIP', 1))

    @classmethod
    def validate_config(cls):
        """Validate critical configuration settings."""
        if not os.path.exists(cls.MODEL_PATH):
            print(f"Warning: Model file not found: {cls.MODEL_PATH}")
        if not os.path.exists(cls.DATA_PATH):
            print(f"Warning: Data file not found: {cls.DATA_PATH}")
        if not os.path.exists(cls.SHAPE_PREDICTOR_PATH):
            print(f"Warning: Shape predictor file not found: {cls.SHAPE_PREDICTOR_PATH}")

        # Ensure logs directory exists
        log_dir = os.path.dirname(cls.LOG_FILE)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)

        print("Configuration validated successfully.")
