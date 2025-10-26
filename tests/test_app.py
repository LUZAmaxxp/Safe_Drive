import unittest
import numpy as np
import cv2
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config
from utils import (
    validate_frame,
    sanitize_emotion_label,
    calculate_sleep_probability,
    safe_release_resources
)

class TestConfig(unittest.TestCase):
    """Test configuration management."""

    def test_config_loading(self):
        """Test that configuration loads from environment variables."""
        # Test default values
        config = Config()
        self.assertEqual(config.APP_NAME, 'Safe_Drive')
        self.assertFalse(config.DEBUG)
        self.assertEqual(config.SECRET_KEY, 'default-secret-key-change-in-production')

class TestUtils(unittest.TestCase):
    """Test utility functions."""

    def test_validate_frame_valid(self):
        """Test frame validation with valid frame."""
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        self.assertTrue(validate_frame(frame))

    def test_validate_frame_invalid(self):
        """Test frame validation with invalid frames."""
        # None frame
        self.assertFalse(validate_frame(None))

        # Wrong shape
        frame = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
        self.assertFalse(validate_frame(frame))

        # Empty frame
        frame = np.array([])
        self.assertFalse(validate_frame(frame))

    def test_sanitize_emotion_label(self):
        """Test emotion label sanitization."""
        # Valid emotions
        self.assertEqual(sanitize_emotion_label('happy'), 'happy')
        self.assertEqual(sanitize_emotion_label('SAD'), 'sad')

        # Invalid emotion
        self.assertEqual(sanitize_emotion_label('invalid_emotion'), 'unknown')

    def test_calculate_sleep_probability(self):
        """Test sleep probability calculation."""
        emotions = {
            'sad': 0.6,
            'neutral': 0.3,
            'happy': 0.1
        }

        prob = calculate_sleep_probability(emotions)
        # Expected: (0.6 * 0.4 + 0.3 * 0.3) / (0.4 + 0.3) = 0.4714
        self.assertAlmostEqual(prob, 0.4714, places=3)

    def test_safe_release_resources(self):
        """Test safe resource release."""
        mock_resource = Mock()
        safe_release_resources(mock_resource)
        mock_resource.release.assert_called_once()

class TestIntegration(unittest.TestCase):
    """Integration tests for the application."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)

    @patch('cv2.VideoCapture')
    def test_camera_initialization(self, mock_cap):
        """Test camera initialization with mock."""
        from utils import secure_camera_capture

        mock_cap_instance = Mock()
        mock_cap_instance.isOpened.return_value = True
        mock_cap.return_value = mock_cap_instance

        cap = secure_camera_capture(0, 1)
        self.assertIsNotNone(cap)
        mock_cap.assert_called_with(0, cv2.CAP_DSHOW)

if __name__ == '__main__':
    # Create test directory if it doesn't exist
    os.makedirs('tests', exist_ok=True)

    # Run tests
    unittest.main(verbosity=2)
