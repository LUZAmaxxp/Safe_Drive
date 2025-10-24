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

## Modifications Made
- **requirements.txt**: Added dependencies including opencv-python, fer, tensorflow, numpy, Pillow, matplotlib, and scikit-learn.
- **main.py**: Created a basic script for capturing webcam feed, detecting emotions using FER, and classifying sleep status based on dominant emotion.
- **TODO.md**: Added a task list for project initialization and future improvements.
- **README.md**: Updated with project description, installation, usage, and this modifications section.

## Future Improvements
- Integrate with vehicle systems for alerts.
- Train a dedicated model for eye closure detection.
- Add drowsiness scoring.

## Dependencies
- opencv-python: For video capture and image processing
- fer: Facial emotion recognition library
- tensorflow: Backend for FER
- numpy, Pillow, matplotlib, scikit-learn: Supporting libraries

## License
MIT License
