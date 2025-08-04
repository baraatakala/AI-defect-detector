# Enhanced Windows setup script for the AI Defect Detector

Write-Host "🚀 Setting up Enhanced AI Building Defect Detector..." -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Check Python version
$pythonVersion = python --version 2>&1
Write-Host "✓ Python version: $pythonVersion" -ForegroundColor Green

# Create virtual environment
Write-Host "📦 Creating virtual environment..." -ForegroundColor Yellow
python -m venv venv
& "venv\Scripts\Activate.ps1"

# Upgrade pip
Write-Host "⬆️  Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install core dependencies first
Write-Host "📚 Installing core dependencies..." -ForegroundColor Yellow
pip install Flask==2.3.3 Werkzeug==2.3.7

# Install document processing
Write-Host "📄 Installing document processing libraries..." -ForegroundColor Yellow
pip install PyMuPDF==1.23.8 python-docx==0.8.11

# Install basic ML dependencies
Write-Host "🧠 Installing machine learning libraries..." -ForegroundColor Yellow
pip install numpy==1.24.3 pandas==2.1.3 scikit-learn==1.3.2

# Try to install PyTorch and Transformers
Write-Host "🤖 Installing advanced ML libraries (this may take a while)..." -ForegroundColor Yellow
try {
    pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu
    pip install transformers==4.35.0
    Write-Host "✓ ML libraries installed successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Advanced ML libraries failed to install (will use rule-based detection)" -ForegroundColor Red
}

# Install image processing (optional)
Write-Host "🖼️  Installing image processing libraries..." -ForegroundColor Yellow
try {
    pip install opencv-python==4.8.1.78 Pillow==10.0.1
    Write-Host "✓ Image processing libraries installed successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Image processing libraries failed to install (optional feature)" -ForegroundColor Red
}

# Install visualization libraries
Write-Host "📊 Installing visualization libraries..." -ForegroundColor Yellow
pip install matplotlib==3.8.2 seaborn==0.12.2

# Install additional utilities
Write-Host "🔧 Installing utilities..." -ForegroundColor Yellow
pip install requests==2.31.0 cryptography==41.0.7

# Install development tools
Write-Host "🧪 Installing development tools..." -ForegroundColor Yellow
pip install pytest==7.4.3 pytest-flask==1.3.0

# Install production server
Write-Host "🌐 Installing production server..." -ForegroundColor Yellow
pip install gunicorn==21.2.0 waitress==2.1.2

# Create necessary directories
Write-Host "📁 Creating project directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "uploads"
New-Item -ItemType Directory -Force -Path "models"
New-Item -ItemType Directory -Force -Path "static"
New-Item -ItemType Directory -Force -Path "templates"

# Initialize database
Write-Host "🗄️  Initializing database..." -ForegroundColor Yellow
python -c "
from app_enhanced import init_database
init_database()
print('Database initialized successfully!')
"

# Create startup script
Write-Host "📝 Creating startup scripts..." -ForegroundColor Yellow

@"
@echo off
call venv\Scripts\activate
echo 🚀 Starting Enhanced AI Defect Detector...
python app_enhanced.py
pause
"@ | Out-File -FilePath "start_enhanced.bat" -Encoding utf8

# Create test script
@"
import os
import sys

def test_imports():
    """Test all critical imports"""
    try:
        import flask
        print("✓ Flask imported successfully")
        
        import fitz
        print("✓ PyMuPDF imported successfully")
        
        import docx
        print("✓ python-docx imported successfully")
        
        try:
            import torch
            import transformers
            print("✓ ML libraries imported successfully")
        except ImportError:
            print("⚠️  ML libraries not available")
        
        try:
            import cv2
            from PIL import Image
            print("✓ Image processing libraries imported successfully")
        except ImportError:
            print("⚠️  Image processing libraries not available")
        
        print("\n🎉 System test completed!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    test_imports()
"@ | Out-File -FilePath "test_system.py" -Encoding utf8

Write-Host ""
Write-Host "🎉 Setup completed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Activate virtual environment: venv\Scripts\activate" -ForegroundColor White
Write-Host "2. Test the system: python test_system.py" -ForegroundColor White
Write-Host "3. Start the application: python app_enhanced.py" -ForegroundColor White
Write-Host "4. Or use startup script: start_enhanced.bat" -ForegroundColor White
Write-Host ""
Write-Host "🌐 The application will be available at: http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Features available:" -ForegroundColor Cyan
Write-Host "- ✅ Document processing (PDF, DOCX)" -ForegroundColor White
Write-Host "- 🧠 Machine Learning detection (if PyTorch installed)" -ForegroundColor White
Write-Host "- 🖼️  Image processing (if OpenCV installed)" -ForegroundColor White
Write-Host "- 📍 Location visualization" -ForegroundColor White
Write-Host "- 📊 Interactive dashboard" -ForegroundColor White
Write-Host ""
Write-Host "For production deployment, use: waitress-serve --host=0.0.0.0 --port=5000 app_enhanced:app" -ForegroundColor Yellow
