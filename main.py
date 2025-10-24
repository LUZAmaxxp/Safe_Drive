from fer import FER
import cv2
import numpy as np

def detect_emotion_and_sleep(frame):
    """
    Detect emotions and determine if the person appears asleep based on eye state.
    """
    # Initialize the emotion detector
    emotion_detector = FER(mtcnn=True)

    # Detect emotions in the frame
    emotions = emotion_detector.detect_emotions(frame)

    if emotions:
        # Get the dominant emotion
        dominant_emotion = max(emotions[0]['emotions'], key=emotions[0]['emotions'].get)

        # For sleep detection, check if eyes are closed (sad or neutral might indicate drowsiness)
        # This is a simplified approach; in reality, you'd train a model on eye states
        if dominant_emotion in ['sad', 'neutral'] or emotions[0]['emotions']['sad'] > 0.5:
            sleep_status = "Possibly Asleep"
        else:
            sleep_status = "Awake"

        return dominant_emotion, sleep_status
    else:
        return "No face detected", "Unknown"

def main():
    # Open webcam (try different indices if 0 doesn't work)
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Could not open webcam at index 0, trying index 1...")
        cap = cv2.VideoCapture(1)
        if not cap.isOpened():
            print("Error: Could not open webcam at any index")
            return

    print("Starting Facial Emotion Recognition for Driver Sleep Detection...")
    print("Press 'q' to quit")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        # Detect emotion and sleep status
        emotion, sleep_status = detect_emotion_and_sleep(frame)

        # Display results on frame
        cv2.putText(frame, f"Emotion: {emotion}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"Status: {sleep_status}", (10, 70), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        # Show the frame
        cv2.imshow('Driver Sleep Detection', frame)

        # Break loop on 'q' key press
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release resources
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
