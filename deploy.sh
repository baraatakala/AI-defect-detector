#!/bin/bash
# deployment.sh - Production deployment script

echo "🚀 Deploying Building Defect Detector..."

# Create production environment file
if [ ! -f .env ]; then
    echo "📝 Creating environment configuration..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your production settings!"
fi

# Install production dependencies
echo "📦 Installing production dependencies..."
pip install -r requirements_production.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p uploads
mkdir -p logs
mkdir -p backups

# Set permissions (Linux/Mac)
if [[ "$OSTYPE" == "linux-gnu"* ]] || [[ "$OSTYPE" == "darwin"* ]]; then
    chmod 755 uploads
    chmod 755 logs
    chmod 644 *.py
fi

# Initialize database
echo "🗄️ Initializing database..."
python -c "
import sqlite3
conn = sqlite3.connect('defect_analysis.db')
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS analyses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        filename TEXT NOT NULL,
        timestamp TEXT NOT NULL,
        total_defects INTEGER,
        defect_summary TEXT,
        defects_detail TEXT
    )
''')
conn.commit()
conn.close()
print('Database initialized successfully!')
"

# Test the application
echo "🧪 Testing application..."
python -c "
from app_production import app
with app.test_client() as client:
    response = client.get('/health')
    if response.status_code == 200:
        print('✅ Health check passed!')
    else:
        print('❌ Health check failed!')
        exit(1)
"

echo "✅ Deployment preparation complete!"
echo ""
echo "🔧 To start the production server:"
echo "   For development: python app_production.py"
echo "   For production:  gunicorn --bind 0.0.0.0:5000 app_production:app"
echo ""
echo "📊 Monitor at: http://localhost:5000/health"
