@echo off
echo.
echo 🚀 DEPLOYING YOUR AMAZING BUILDING DEFECT DETECTOR WEBSITE!
echo ================================================================
echo.

cd /d "c:\Users\isc\VS_Code\ai_file_processor"

echo 📋 Quick system check...
C:/Users/isc/VS_Code/.venv/Scripts/python.exe -c "print('✅ Python environment ready')"

echo 🗄️  Initializing database...
C:/Users/isc/VS_Code/.venv/Scripts/python.exe -c "from app_fixed import init_database; init_database(); print('✅ Database initialized')"

echo.
echo 🌐 STARTING YOUR WEBSITE...
echo ================================================================
echo.
echo 🎉 Your website will be available at:
echo.
echo     👉 http://localhost:5000
echo.
echo 💡 Features ready:
echo     ✅ Document Upload (PDF, DOCX)
echo     ✅ AI Defect Detection
echo     ✅ Interactive Dashboard
echo     ✅ Beautiful Charts & Visualizations
echo     ✅ Export & Print Reports
echo.
echo 📋 Controls:
echo     • Press Ctrl+C to stop the server
echo     • Keep this window open while using the website
echo.
echo ⏰ Starting server now...
echo.

C:/Users/isc/VS_Code/.venv/Scripts/python.exe app_fixed.py
