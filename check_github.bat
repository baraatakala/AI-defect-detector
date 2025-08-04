@echo off
echo ==========================================
echo   CHECKING GITHUB REPOSITORY STATUS
echo ==========================================

cd /d "c:\Users\isc\VS_Code\ai_file_processor"

echo [1/3] Checking git status...
git status

echo.
echo [2/3] Checking remote repositories...
git remote -v

echo.
echo [3/3] Checking latest commits...
git log --oneline -3

echo.
echo 🌐 Your GitHub repository should be at:
echo    https://github.com/baraatakala/defect-detector
echo.
echo 📋 Files that should be visible on GitHub:
echo    ✓ app_production.py (main Flask app)
echo    ✓ templates/analysis_detail_final.html (clean template)
echo    ✓ templates/dashboard_simple.html (with delete buttons)
echo    ✓ requirements.txt (Railway dependencies)
echo    ✓ Procfile (Railway configuration)
echo    ✓ README.md (documentation)
echo.
pause
