import logging
import os
from config import Config

def setup_logger(name: str = 'safe_drive', level: str = None, log_file: str = None) -> logging.Logger:
    """
    Set up a secure logger with proper formatting and file handling.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file

    Returns:
        Configured logger instance
    """
    if level is None:
        level = Config.LOG_LEVEL
    if log_file is None:
        log_file = Config.LOG_FILE

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper(), logging.INFO))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s - %(message)s'
    )

    # File handler with secure permissions
    if log_file:
        try:
            log_dir = os.path.dirname(log_file)
            if log_dir and not os.path.exists(log_dir):
                os.makedirs(log_dir, exist_ok=True)

            file_handler = logging.FileHandler(log_file)
            file_handler.setLevel(getattr(logging, level.upper(), logging.INFO))
            file_handler.setFormatter(file_formatter)
            logger.addHandler(file_handler)

            # Set secure file permissions (if on Unix-like system)
            try:
                os.chmod(log_file, 0o600)  # Owner read/write only
            except OSError:
                pass  # Skip on Windows or if permission denied

        except (OSError) as e:
            print(f"Warning: Could not set up file logging: {e}")

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # Only warnings and above to console
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)

    return logger

# Global logger instance
logger = setup_logger()
