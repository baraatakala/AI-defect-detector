@echo off
echo ===========================================
echo   BUILDING DEFECT DETECTOR - CLEAN DEPLOY
echo ===========================================
echo.

echo [1/5] Activating Python environment...
call venv\Scripts\activate.bat

echo [2/5] Installing/updating dependencies...
pip install -r requirements.txt

echo [3/5] Starting Flask application...
echo.
echo ✅ Application ready! 
echo 🌐 Open your browser to: http://localhost:5000
echo 📊 Dashboard available at: http://localhost:5000/dashboard
echo.
echo 🔥 Your enhanced defect detector is now running with:
echo    ✓ Machine Learning integration
echo    ✓ Image processing capabilities  
echo    ✓ Professional Bootstrap 5 design
echo    ✓ Clean code (0 VS Code errors!)
echo    ✓ CSV export functionality
echo    ✓ Real-time analytics
echo.
echo Press Ctrl+C to stop the server
echo.

python app_fixed.py
