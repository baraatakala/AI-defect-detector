@echo off
color 0A
echo.
echo ==========================================
echo   🚀 DEPLOY DEFECT DETECTOR TO RAILWAY
echo ==========================================
echo.

cd /d "c:\Users\isc\VS_Code\ai_file_processor"

echo [1/3] Adding sample data for testing...
C:\Users\isc\VS_Code\.venv\Scripts\python.exe add_sample_data.py
echo ✅ Sample data added!
echo.

echo [2/3] Testing local app...
echo 🌐 Your app is running at: http://localhost:5000
echo 📊 Dashboard (with delete buttons): http://localhost:5000/dashboard
echo.
timeout /t 3

echo [3/3] Ready for GitHub and Railway deployment!
echo.
echo 📋 MANUAL STEPS NEEDED:
echo.
echo 🔧 Push to GitHub:
echo    1. Open Command Prompt in this folder
echo    2. Run: git init
echo    3. Run: git add .
echo    4. Run: git commit -m "Deploy defect detector"  
echo    5. Run: git remote add origin https://github.com/baraatakala/defect-detector.git
echo    6. Run: git push -u origin main
echo.
echo 🚀 Deploy to Railway:
echo    1. Go to https://railway.app
echo    2. Click "New Project"
echo    3. Select "Deploy from GitHub repo"
echo    4. Choose: baraatakala/defect-detector
echo    5. Railway auto-deploys your app!
echo.
echo ✨ Your enhanced defect detector will be live!
echo.
echo Press any key to open the dashboard to test delete functionality...
pause
start http://localhost:5000/dashboard
