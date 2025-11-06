#!/bin/bash
# Docker run script for Safe Drive with streaming support

echo "Safe Drive Docker Launcher"
echo "========================="
echo ""
echo "This script helps you run Safe Drive with proper network configuration"
echo "for streaming mode (Method 2 with OBS)."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Creating default .env file..."
    cat > .env << EOF
# Safe Drive Configuration
USE_STREAM=True
STREAM_URL=http://host.docker.internal:8080/stream.mjpg
STREAM_TYPE=mjpeg
CAMERA_INDEX=0
MAX_FPS=30
EOF
fi

echo "Current configuration:"
cat .env
echo ""

# Function to run on Linux
run_linux() {
    echo "Running on Linux..."
    docker run -it --rm \
        --add-host=host.docker.internal:host-gateway \
        -p 5000:5000 \
        --env-file .env \
        safe-drive
}

# Function to run on Windows (Docker Desktop)
run_windows() {
    echo "Running on Windows (Docker Desktop)..."
    docker run -it --rm \
        -p 5000:5000 \
        --env-file .env \
        safe-drive
}

# Function to run with custom stream URL
run_custom() {
    echo "Enter your stream URL (e.g., http://localhost:8080/stream.mjpg):"
    read stream_url
    
    # Update .env file
    sed -i.bak "s|STREAM_URL=.*|STREAM_URL=$stream_url|" .env
    
    echo "Running with custom stream URL: $stream_url"
    docker run -it --rm \
        -p 5000:5000 \
        --env-file .env \
        safe-drive
}

# Main menu
echo "Choose your platform:"
echo "1) Linux"
echo "2) Windows (Docker Desktop)"
echo "3) Custom stream URL"
echo "4) Exit"
echo ""
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        run_linux
        ;;
    2)
        run_windows
        ;;
    3)
        run_custom
        ;;
    4)
        echo "Exiting..."
        exit 0
        ;;
    *)
        echo "Invalid choice. Exiting..."
        exit 1
        ;;
esac