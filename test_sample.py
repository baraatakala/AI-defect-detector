#!/usr/bin/env python3
"""
Quick test of the Building Defect Detector with sample data
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app_simple import detect_defects, clean_and_preprocess_text

def test_sample_file():
    """Test with the sample building survey"""
    print("🏗️ Testing Building Defect Detector")
    print("=" * 50)
    
    # Read sample file
    with open('sample_building_survey.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    
    print(f"📄 Loaded sample file ({len(content)} characters)")
    
    # Clean text
    cleaned = clean_and_preprocess_text(content)
    print(f"🧹 Cleaned text ({len(cleaned)} characters)")
    
    # Detect defects
    defects = detect_defects(cleaned)
    print(f"🔍 Found {len(defects)} defects")
    print()
    
    # Show results
    if defects:
        summary = {}
        for i, defect in enumerate(defects, 1):
            print(f"{i}. {defect['type']} - Severity: {defect['severity']}")
            print(f"   Keyword: '{defect['keyword']}'")
            print(f"   Context: {defect['sentence'][:100]}...")
            print()
            
            # Count by type
            defect_type = defect['type']
            summary[defect_type] = summary.get(defect_type, 0) + 1
        
        print("📊 Summary by Category:")
        for category, count in summary.items():
            print(f"   {category}: {count} issues")
    else:
        print("❌ No defects detected!")
    
    print("\n✅ Test completed!")
    print("💡 This sample content should work perfectly in your web app!")

if __name__ == "__main__":
    test_sample_file()
