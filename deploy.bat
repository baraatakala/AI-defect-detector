@echo off
REM deploy.bat - Windows deployment script for Building Defect Detector

echo 🚀 Deploying Building Defect Detector...

REM Create production environment file
if not exist .env (
    echo 📝 Creating environment configuration...
    copy .env.example .env
    echo ⚠️  Please edit .env file with your production settings!
)

REM Install production dependencies
echo 📦 Installing production dependencies...
pip install -r requirements_production.txt

REM Create necessary directories
echo 📁 Creating directories...
if not exist uploads mkdir uploads
if not exist logs mkdir logs
if not exist backups mkdir backups

REM Initialize database
echo 🗄️ Initializing database...
python -c "import sqlite3; conn = sqlite3.connect('defect_analysis.db'); cursor = conn.cursor(); cursor.execute('CREATE TABLE IF NOT EXISTS analyses (id INTEGER PRIMARY KEY AUTOINCREMENT, filename TEXT NOT NULL, timestamp TEXT NOT NULL, total_defects INTEGER, defect_summary TEXT, defects_detail TEXT)'); conn.commit(); conn.close(); print('Database initialized successfully!')"

REM Test the application
echo 🧪 Testing application...
python -c "from app_production import app; client = app.test_client(); response = client.get('/health'); print('✅ Health check passed!' if response.status_code == 200 else '❌ Health check failed!')"

echo ✅ Deployment preparation complete!
echo.
echo 🔧 To start the server:
echo    python app_production.py
echo.
echo 📊 Monitor at: http://localhost:5000/health
pause
