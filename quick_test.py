# quick_test.py
# Quick test of the enhanced defect detector

import sys
import os
print("🧪 Testing Enhanced Defect Detector")
print("=" * 50)

# Test 1: Import test
print("\n1. Testing imports...")
try:
    from ml_defect_detector_simple import HybridDefectDetector
    print("✅ ML detector imported successfully")
except Exception as e:
    print(f"❌ ML detector import failed: {e}")

# Test 2: Basic functionality
print("\n2. Testing defect detection...")
try:
    detector = HybridDefectDetector()
    capabilities = detector.get_capabilities()
    print(f"✅ Detector initialized: {capabilities}")
    
    # Test with sample text
    sample_text = """
    The foundation shows visible cracks along the east wall, measuring approximately 2mm wide.
    Significant damp was observed in the basement area with moisture buildup on the concrete walls.
    The electrical wiring in the main panel appears to be corroded, with several connections showing signs of oxidation.
    Mold growth was detected on the north-facing exterior wall.
    The main water pipe running through the basement shows signs of minor leakage at the joint connections.
    """
    
    defects = detector.detect_defects(sample_text)
    print(f"✅ Defects detected: {len(defects)}")
    
    for i, defect in enumerate(defects[:3], 1):
        print(f"   {i}. {defect['type']} - {defect['confidence']:.2f} confidence")
    
except Exception as e:
    print(f"❌ Detection test failed: {e}")

# Test 3: File processing
print("\n3. Testing file processing...")
try:
    import fitz  # PyMuPDF
    from docx import Document
    print("✅ Document processing libraries available")
except Exception as e:
    print(f"❌ Document processing failed: {e}")

# Test 4: Flask app import
print("\n4. Testing Flask app...")
try:
    from app_fixed import app
    print("✅ Flask app imported successfully")
except Exception as e:
    print(f"❌ Flask app import failed: {e}")

print("\n" + "=" * 50)
print("🎉 Test completed!")
print("\nNext steps:")
print("1. Run: python app_fixed.py")
print("2. Open: http://localhost:5000")
print("3. Upload your sample survey document")
