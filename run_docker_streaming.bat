@echo off
echo Safe Drive Docker Launcher for Windows
echo ======================================
echo.
echo This script helps you run Safe Drive with proper network configuration
echo for streaming mode (Method 2 with OBS).
echo.

REM Check if .env file exists
if not exist .env (
    echo Creating default .env file...
    (
        echo # Safe Drive Configuration
        echo USE_STREAM=True
        echo STREAM_URL=http://host.docker.internal:8080/stream.mjpg
        echo STREAM_TYPE=mjpeg
        echo CAMERA_INDEX=0
        echo MAX_FPS=30
    ) > .env
)

echo Current configuration:
type .env
echo.

echo Rebuilding Docker image with no-cache to apply updates...
docker build --no-cache -t safe-drive . 
IF %ERRORLEVEL% NEQ 0 (
    echo Docker build failed. Aborting.
    exit /b %ERRORLEVEL%
)
echo.

REM Function to run with default settings
:run_default
echo Running with default settings...
docker run -it --rm -p 5000:5000 --env-file .env safe-drive
goto :eof

REM Function to run with custom stream URL
:run_custom
echo Enter your stream URL (e.g., http://localhost:8080/stream.mjpg):
set /p stream_url=

REM Update .env file
(
    echo # Safe Drive Configuration
    echo USE_STREAM=True
    echo STREAM_URL=%stream_url%
    echo STREAM_TYPE=mjpeg
    echo CAMERA_INDEX=0
    echo MAX_FPS=30
) > .env

echo Running with custom stream URL: %stream_url%
docker run -it --rm -p 5000:5000 --env-file .env safe-drive
goto :eof

REM Main menu
echo Choose an option:
echo 1) Run with default settings (localhost:8080)
echo 2) Run with custom stream URL
echo 3) Exit
echo.
set /p choice=Enter your choice (1-3): 

if "%choice%"=="1" goto run_default
if "%choice%"=="2" goto run_custom
if "%choice%"=="3" (
    echo Exiting...
    exit /b 0
)
echo Invalid choice. Exiting...
exit /b 1