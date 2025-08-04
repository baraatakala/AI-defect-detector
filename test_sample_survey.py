# test_sample_survey.py
# Test the sample survey document with our enhanced detector

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from ml_defect_detector_simple import HybridDefectDetector
    
    print("🏢 Testing Building Survey Analysis")
    print("=" * 60)
    
    # Initialize detector
    detector = HybridDefectDetector()
    capabilities = detector.get_capabilities()
    
    print(f"🔧 System Capabilities: {capabilities}")
    print()
    
    # Read the sample survey document
    sample_file = "sample_building_survey.txt"
    if os.path.exists(sample_file):
        with open(sample_file, 'r', encoding='utf-8') as f:
            survey_text = f.read()
        
        print(f"📄 Sample document loaded: {len(survey_text)} characters")
        print()
        
        # Analyze the document
        defects = detector.detect_defects(survey_text)
        
        print(f"🔍 Analysis Results:")
        print(f"   Total defects found: {len(defects)}")
        print()
        
        # Group defects by type
        defect_counts = {}
        for defect in defects:
            defect_type = defect['type']
            defect_counts[defect_type] = defect_counts.get(defect_type, 0) + 1
        
        print("📊 Defect Distribution:")
        for defect_type, count in sorted(defect_counts.items()):
            print(f"   {defect_type}: {count} instances")
        print()
        
        print("🔍 Detailed Findings:")
        print("-" * 40)
        
        for i, defect in enumerate(defects, 1):
            confidence_pct = defect['confidence'] * 100
            method = defect.get('detection_method', 'unknown')
            
            print(f"{i:2d}. {defect['type']}")
            print(f"    Confidence: {confidence_pct:.1f}%")
            print(f"    Severity: {defect.get('severity', 'Medium')}")
            print(f"    Method: {method}")
            print(f"    Text: {defect['sentence'][:100]}...")
            print()
        
        # Calculate statistics
        avg_confidence = sum(d['confidence'] for d in defects) / len(defects) if defects else 0
        high_confidence = len([d for d in defects if d['confidence'] > 0.7])
        
        print("📈 Summary Statistics:")
        print(f"   Average confidence: {avg_confidence * 100:.1f}%")
        print(f"   High confidence detections: {high_confidence}/{len(defects)}")
        print(f"   Detection categories: {len(defect_counts)}")
        
        # Simulate the defect categories from your evaluation
        expected_categories = ['Cracks', 'Damp', 'Corrosion', 'Mold', 'Structural', 'Electrical', 'Plumbing']
        found_categories = set(defect_counts.keys())
        coverage = len(found_categories.intersection(expected_categories)) / len(expected_categories)
        
        print(f"   Category coverage: {coverage * 100:.1f}%")
        print()
        
        print("✅ Analysis Complete!")
        print(f"This sample would show {len(defects)} defects in your web interface")
        
    else:
        print(f"❌ Sample file '{sample_file}' not found")
        print("Please ensure the sample survey document is in the current directory")

except Exception as e:
    print(f"❌ Error during testing: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("🌐 To test in the web interface:")
print("1. Run: python app_fixed.py")
print("2. Open: http://localhost:5000")
print("3. Upload the sample_building_survey.txt file")
print("4. Or click 'Test with Sample Document' button")
