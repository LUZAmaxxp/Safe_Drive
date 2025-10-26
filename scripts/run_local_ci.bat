@echo off
REM Local CI Runner Script for Windows
REM Run this script to perform CI checks locally before pushing

echo ================================================
echo Safe_Drive Local CI Check
echo ================================================
echo.

REM Check Python
echo Checking Python syntax...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python not found
    exit /b 1
) else (
    echo [OK] Python found
    python --version
)

REM Check Python syntax
echo.
echo Checking Python syntax in all .py files...
for %%f in (*.py) do (
    python -m py_compile "%%f" >nul 2>&1
    if !errorlevel! equ 0 (
        echo [OK] %%f
    ) else (
        echo [ERROR] %%f has syntax errors
    )
)

REM Check requirements.txt
if exist requirements.txt (
    echo.
    echo requirements.txt found
    echo   - To install: pip install -r requirements.txt
) else (
    echo [WARNING] requirements.txt not found
)

REM Check Node.js and frontend
echo.
echo Checking frontend...
where node >nul 2>&1
if %errorlevel% equ 0 (
    echo [OK] Node.js version:
    node --version
    
    if exist "frontend\package.json" (
        echo.
        echo Frontend directory found
        echo   - To install: cd frontend ^&^& npm install
        echo   - To build: cd frontend ^&^& npm run build
    ) else (
        echo [ERROR] Frontend package.json not found
    )
) else (
    echo [WARNING] Node.js not found (frontend checks skipped)
)

REM Check for tests
echo.
echo Checking tests...
if exist "tests\test_app.py" (
    echo [OK] Test file found: tests\test_app.py
    echo   - To run tests: python -m unittest tests.test_app -v
) else (
    echo [WARNING] Test file not found
)

REM Summary
echo.
echo ================================================
echo Local CI Check Complete
echo ================================================
echo.
echo To run full tests:
echo   1. Install Python dependencies: pip install -r requirements.txt
echo   2. Run tests: python -m unittest tests.test_app -v
echo.
echo To build frontend:
echo   1. cd frontend
echo   2. npm install
echo   3. npm run build
echo.

pause

