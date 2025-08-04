#!/bin/bash
# Enhanced setup script for the AI Defect Detector

echo "🚀 Setting up Enhanced AI Building Defect Detector..."
echo "=================================================="

# Check Python version
python_version=$(python3 --version 2>&1)
echo "✓ Python version: $python_version"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install core dependencies first
echo "📚 Installing core dependencies..."
pip install Flask==2.3.3 Werkzeug==2.3.7

# Install document processing
echo "📄 Installing document processing libraries..."
pip install PyMuPDF==1.23.8 python-docx==0.8.11

# Install basic ML dependencies
echo "🧠 Installing machine learning libraries..."
pip install numpy==1.24.3 pandas==2.1.3 scikit-learn==1.3.2

# Try to install PyTorch and Transformers
echo "🤖 Installing advanced ML libraries (this may take a while)..."
pip install torch==2.1.0 --index-url https://download.pytorch.org/whl/cpu
pip install transformers==4.35.0

# Install image processing (optional)
echo "🖼️  Installing image processing libraries..."
pip install opencv-python==4.8.1.78 Pillow==10.0.1 || echo "⚠️  Image processing libraries failed to install (optional)"

# Install visualization libraries
echo "📊 Installing visualization libraries..."
pip install matplotlib==3.8.2 seaborn==0.12.2

# Install additional utilities
echo "🔧 Installing utilities..."
pip install requests==2.31.0 cryptography==41.0.7

# Install development tools
echo "🧪 Installing development tools..."
pip install pytest==7.4.3 pytest-flask==1.3.0

# Install production server
echo "🌐 Installing production server..."
pip install gunicorn==21.2.0 waitress==2.1.2

# Create necessary directories
echo "📁 Creating project directories..."
mkdir -p uploads
mkdir -p models
mkdir -p static
mkdir -p templates

# Initialize database
echo "🗄️  Initializing database..."
python3 -c "
from app_enhanced import init_database
init_database()
print('Database initialized successfully!')
"

# Create startup script
echo "📝 Creating startup scripts..."
cat > start_enhanced.sh << 'EOF'
#!/bin/bash
source venv/bin/activate
echo "🚀 Starting Enhanced AI Defect Detector..."
python3 app_enhanced.py
EOF

cat > start_enhanced.bat << 'EOF'
@echo off
call venv\Scripts\activate
echo Starting Enhanced AI Defect Detector...
python app_enhanced.py
pause
EOF

chmod +x start_enhanced.sh

# Create test script
cat > test_system.py << 'EOF'
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
EOF

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "Next steps:"
echo "1. Activate virtual environment: source venv/bin/activate (Linux/Mac) or venv\\Scripts\\activate (Windows)"
echo "2. Test the system: python3 test_system.py"
echo "3. Start the application: python3 app_enhanced.py"
echo "4. Or use startup script: ./start_enhanced.sh (Linux/Mac) or start_enhanced.bat (Windows)"
echo ""
echo "🌐 The application will be available at: http://localhost:5000"
echo ""
echo "Features available:"
echo "- ✅ Document processing (PDF, DOCX)"
echo "- 🧠 Machine Learning detection (if PyTorch installed)"
echo "- 🖼️  Image processing (if OpenCV installed)"
echo "- 📍 Location visualization"
echo "- 📊 Interactive dashboard"
echo ""
echo "For production deployment, use: gunicorn -w 4 -b 0.0.0.0:5000 app_enhanced:app"
