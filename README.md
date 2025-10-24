# Facial Emotion Recognition for Driver Sleep Detection

This project aims to build a Facial Emotion Recognition (FER) system specifically designed to detect if a driver is asleep or awake, promoting safer driving practices.

## Features
- Real-time facial emotion detection using webcam
- Classification of sleep status based on detected emotions (simplified model)
- Easy-to-use Python script

## Requirements
- Python 3.8+
- Webcam

## Installation
1. Clone or download this repository.
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage
Run the main script:
```
python main.py
```
- The application will open your webcam and start detecting emotions.
- It will display the dominant emotion and sleep status on the video feed.
- Press 'q' to quit.

## How It Works
- Uses the FER library for emotion detection.
- Simplifies sleep detection by checking for emotions like 'sad' or 'neutral' which might indicate drowsiness.
- Note: This is a basic implementation. For production, train a custom model on eye states for better accuracy.

## Security Best Practices Implemented
- **Environment Configuration**: Added `.env` file for secure configuration management with `python-dotenv`.
- **Configuration Management**: Created `config.py` for centralized, validated configuration loading.
- **Secure Logging**: Implemented `logger.py` with proper log levels, file permissions, and secure file handling.
- **Input Validation**: Added `utils.py` with frame validation, emotion sanitization, and secure resource management.
- **Secure Application Structure**: Refactored `main.py` into `main_secure.py` with proper error handling, resource cleanup, and security measures.
- **Unit Tests**: Added `tests/test_app.py` with comprehensive test coverage for utilities and configuration.
- **Git Security**: Added `.gitignore` to prevent sensitive files from being committed.

## Modifications Made
- **requirements.txt**: Added dependencies including opencv-python, fer, tensorflow, numpy, Pillow, matplotlib, scikit-learn, and python-dotenv.
- **main.py**: Original basic script for capturing webcam feed, detecting emotions using FER, and classifying sleep status.
- **main_secure.py**: Secure version of the application with proper error handling, logging, and resource management.
- **config.py**: Configuration management with environment variable loading and validation.
- **logger.py**: Secure logging implementation with file permissions and proper formatting.
- **utils.py**: Utility functions for secure camera handling, input validation, and resource cleanup.
- **tests/test_app.py**: Unit tests for configuration, utilities, and integration testing.
- **.env**: Environment configuration file (not committed to version control).
- **.gitignore**: Security-focused ignore file to prevent sensitive data exposure.
- **models/train_model.py**: Added a script to download FER2013 dataset and train a CNN model for emotion recognition.
- **models/emotion_model.h5**: Generated an untrained emotion recognition model using TensorFlow/Keras.
- **models/emotion_model_trained.h5**: Trained emotion recognition model on a sample dataset (validation accuracy: 0.1000).
- **data/fer2013.csv**: Sample FER2013 dataset created for training demonstration.
- **TODO.md**: Added a task list for project initialization and future improvements.
- **README.md**: Updated with project description, installation, usage, security practices, and modifications section.

## Future Improvements
- Integrate with vehicle systems for alerts.
- Train a dedicated model for eye closure detection.
- Add drowsiness scoring.

## Dependencies
- opencv-python: For video capture and image processing
- fer: Facial emotion recognition library
- tensorflow: Backend for FER
- numpy, Pillow, matplotlib, scikit-learn: Supporting libraries  
## Pysonar 
to test the quality of code using sonarQube  

pysonar \
  --sonar-host-url=http://localhost:9000 \
  --sonar-token=sqp_6a52ab009b9e6bca63edac33dc6935f18b3d7901 \
  --sonar-project-key=safe_Drive

## License
MIT License
