# Quick deployment check
import os
import sys

print("🚀 Quick Deployment Check")
print("=" * 40)

try:
    # Test core imports
    from app_fixed import app, init_database
    from ml_defect_detector_simple import HybridDefectDetector
    
    print("✅ All imports successful")
    
    # Initialize database
    init_database()
    print("✅ Database ready")
    
    # Test detector
    detector = HybridDefectDetector()
    capabilities = detector.get_capabilities()
    print(f"✅ ML System: {capabilities}")
    
    print("\n🎉 DEPLOYMENT READY!")
    print("\nTo start your website:")
    print("1. Double-click: DEPLOY_NOW.bat")
    print("2. Or run: python app_fixed.py")
    print("3. Open: http://localhost:5000")
    
except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTrying basic startup anyway...")

print("\n" + "=" * 40)
