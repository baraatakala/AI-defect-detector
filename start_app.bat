@echo off
echo 🚀 Starting Enhanced Building Defect Detector
echo ============================================

cd /d "c:\Users\isc\VS_Code\ai_file_processor"

echo 📋 Running quick system test...
C:/Users/isc/VS_Code/.venv/Scripts/python.exe quick_test.py

echo.
echo 🌐 Starting Flask application...
echo The application will be available at: http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo.

C:/Users/isc/VS_Code/.venv/Scripts/python.exe app_fixed.py

pause
