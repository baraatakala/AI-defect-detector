@echo off
echo ==========================================
echo   PUSHING TO GITHUB REPOSITORY
echo ==========================================

cd /d "c:\Users\isc\VS_Code\ai_file_processor"

echo [1/6] Initializing Git repository...
git init
if %ERRORLEVEL% NEQ 0 (
    echo Error: Git init failed
    pause
    exit /b 1
)

echo [2/6] Adding all files...
git add .
if %ERRORLEVEL% NEQ 0 (
    echo Error: Git add failed
    pause
    exit /b 1
)

echo [3/6] Committing files...
git commit -m "Initial commit - Enhanced AI Building Defect Detector with delete functionality"
if %ERRORLEVEL% NEQ 0 (
    echo Error: Git commit failed
    pause
    exit /b 1
)

echo [4/6] Setting main branch...
git branch -M main
if %ERRORLEVEL% NEQ 0 (
    echo Error: Branch setup failed
    pause
    exit /b 1
)

echo [5/6] Adding GitHub remote...
git remote add origin https://github.com/baraatakala/defect-detector.git
if %ERRORLEVEL% NEQ 0 (
    echo Error: Remote add failed (might already exist)
)

echo [6/6] Pushing to GitHub...
git push -u origin main
if %ERRORLEVEL% NEQ 0 (
    echo Error: Push failed - check your GitHub credentials
    echo You might need to authenticate with GitHub
    pause
    exit /b 1
)

echo.
echo ✅ SUCCESS! Code pushed to GitHub repository:
echo    https://github.com/baraatakala/defect-detector
echo.
echo 🚀 Next steps:
echo    1. Go to railway.app
echo    2. Click "New Project"
echo    3. Select "Deploy from GitHub repo"
echo    4. Choose "baraatakala/defect-detector"
echo    5. Railway will auto-deploy your app!
echo.
pause
