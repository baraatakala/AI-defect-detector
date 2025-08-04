#!/usr/bin/env python3
"""
Test script for Building Defect Detector
"""

import os
import sys
import tempfile
from io import BytesIO

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_import():
    """Test if the app can be imported"""
    try:
        from app_simple import app, detect_defects, clean_and_preprocess_text
        print("✅ App imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import app: {e}")
        return False

def test_defect_detection():
    """Test the defect detection functionality"""
    try:
        from app_simple import detect_defects
        
        # Test sample text with known defects
        test_text = """
        The building inspection revealed several concerning issues. 
        There are visible cracks in the foundation wall near the entrance.
        Signs of damp were observed in the basement area with moisture buildup.
        The electrical wiring appears to be corroded in several locations.
        Mold growth was detected in the bathroom ceiling.
        Structural damage to the main support beam requires immediate attention.
        """
        
        defects = detect_defects(test_text)
        print(f"✅ Detected {len(defects)} defects in test text")
        
        for defect in defects:
            print(f"   - {defect['type']}: {defect['keyword']}")
            
        return len(defects) > 0
    except Exception as e:
        print(f"❌ Defect detection test failed: {e}")
        return False

def test_text_preprocessing():
    """Test text cleaning and preprocessing"""
    try:
        from app_simple import clean_and_preprocess_text
        
        test_text = """
        Page 1
        
        Building Survey Report
        123
        
        The property shows signs of deterioration.
        
        
        456
        End of Report
        """
        
        cleaned = clean_and_preprocess_text(test_text)
        print("✅ Text preprocessing working")
        print(f"   Original lines: {len(test_text.split('\\n'))}")
        print(f"   Cleaned lines: {len(cleaned.split('\\n'))}")
        return True
    except Exception as e:
        print(f"❌ Text preprocessing test failed: {e}")
        return False

def test_flask_routes():
    """Test Flask routes"""
    try:
        from app_simple import app
        
        with app.test_client() as client:
            # Test home page
            response = client.get('/')
            assert response.status_code == 200
            print("✅ Home page route working")
            
            # Test upload page
            response = client.get('/upload')
            assert response.status_code == 200
            print("✅ Upload page route working")
            
            # Test dashboard
            response = client.get('/dashboard')
            assert response.status_code == 200
            print("✅ Dashboard route working")
            
        return True
    except Exception as e:
        print(f"❌ Flask routes test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🏗️  Testing Building Defect Detector App")
    print("=" * 50)
    
    tests = [
        test_app_import,
        test_text_preprocessing,
        test_defect_detection,
        test_flask_routes
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"❌ Test {test.__name__} crashed: {e}")
    
    print("=" * 50)
    print(f"Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your app is ready.")
        print("\\n📝 Next steps:")
        print("   1. Install dependencies: pip install -r requirements.txt")
        print("   2. Run the app: python app.py")
        print("   3. Open http://localhost:5000 in your browser")
    else:
        print("⚠️  Some tests failed. Check the error messages above.")

if __name__ == "__main__":
    main()
