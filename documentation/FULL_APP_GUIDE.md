# Full Application Setup Guide: Safe Drive

This guide provides step-by-step instructions to run the complete Safe Drive application, including the backend, frontend, and OBS streaming.

## Architecture Overview

The full application consists of three main parts:

1.  **Backend (Python/Flask)**: Runs in a Docker container, processes the video stream, and performs emotion/drowsiness detection.
2.  **Frontend (React)**: A web interface that displays the video feed and detection results.
3.  **OBS Studio**: Captures your camera and streams it to the backend.

Here's how they work together:

-   **OBS** captures your camera and sends it as an MJPEG stream to a local server.
-   The **Backend** (in Docker) connects to this stream, processes the video, and exposes a Flask API.
-   The **Frontend** (React) communicates with the Flask API to display the video and results in your browser.

## Prerequisites

-   **Docker Desktop**: Installed and running.
-   **OBS Studio**: Installed.
-   **Node.js and npm**: Installed for running the React frontend.
-   **Python**: Installed for the streaming server.

## Step 1: Start the Streaming Server

This server takes your camera feed and makes it available as a network stream.

1.  Open a terminal or command prompt.
2.  Navigate to the `Safe_Drive` directory.
3.  Run the streaming server:

    ```bash
   python streaming_server.py --port 8080 --camera <index>
    ```

    You should see output indicating the server has started on port 8080.

## Step 2: Configure and Start OBS

1.  **Open OBS Studio**.
2.  Follow the `OBS_SETUP_GUIDE.md` to configure OBS to stream your camera to `http://localhost:8080/stream.mjpg`.
3.  **Start streaming** in OBS.

## Step 3: Run the Backend Docker Container

1.  Open a **new** terminal or command prompt.
2.  Navigate to the `Safe_Drive` directory.
3.  Use the provided script to run the Docker container:

    -   **On Windows**:

        ```bash
        run_docker_streaming.bat
        ```

    -   **On Linux**:

        ```bash
        ./run_docker_streaming.sh
        ```

    This will build the Docker image (if it doesn't exist) and start the container.

## Step 4: Run the React Frontend

1.  Open a **third** terminal or command prompt.
2.  Navigate to the `frontend` directory inside the `Safe_Drive` project:

    ```bash
    cd frontend
    ```

3.  Install the necessary packages:

    ```bash
    npm install
    ```

4.  Start the React development server:

    ```bash
    npm start
    ```

    This will automatically open a new browser tab with the Safe Drive application at `http://localhost:3000`.

## Step 5: Verify Everything is Working

1.  **Browser**: The Safe Drive application should be running at `http://localhost:3000`.
2.  **Video Feed**: You should see your camera feed in the browser.
3.  **Detection**: The application should be detecting your face and displaying emotion/drowsiness status.

## Summary of Terminals

You will have three terminals running simultaneously:

-   **Terminal 1**: Running `python streaming_server.py`.
-   **Terminal 2**: Running the Docker container (`run_docker_streaming.bat` or `./run_docker_streaming.sh`).
-   **Terminal 3**: Running the React frontend (`npm start` in the `frontend` directory).

## Troubleshooting

-   **Frontend not connecting to backend**: Ensure the backend container is running and that there are no CORS errors in the browser's developer console.
-   **No video feed**: Make sure OBS is streaming and the `streaming_server.py` is running. Check that the stream URL in your `.env` file is correct.
-   **Docker errors**: Ensure Docker Desktop is running and that you have sufficient permissions.