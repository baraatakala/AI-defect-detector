@echo off
echo Starting Building Defect Detector...
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.7+ and try again
    pause
    exit /b 1
)

REM Check if requirements are installed
echo Checking dependencies...
python -c "import flask" >nul 2>&1
if %errorlevel% neq 0 (
    echo Installing dependencies...
    pip install -r requirements.txt
    if %errorlevel% neq 0 (
        echo Error: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Create uploads directory if it doesn't exist
if not exist "uploads" mkdir uploads

REM Run the application
echo.
echo Starting Flask application...
echo Open your browser and go to: http://localhost:5000
echo Press Ctrl+C to stop the server
echo.
python app.py

pause
