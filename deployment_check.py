#!/usr/bin/env python3
"""
Pre-deployment verification script
Checks all components before deployment to Railway
"""

import sys
import sqlite3
import os
from pathlib import Path

def check_imports():
    """Test all critical imports"""
    try:
        import app_fixed
        print("✅ app_fixed.py imports successfully")
        
        import ml_defect_detector_simple
        print("✅ ML detector imports successfully")
        
        import flask
        print("✅ Flask available")
        
        import fitz  # PyMuPDF
        print("✅ PyMuPDF available")
        
        from docx import Document
        print("✅ python-docx available")
        
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

def check_database():
    """Check database schema and sample data"""
    try:
        conn = sqlite3.connect('defect_analysis.db')
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        if 'analysis' not in tables:
            print("❌ Analysis table missing")
            return False
        print("✅ Analysis table exists")
        
        if 'defects' not in tables:
            print("❌ Defects table missing")
            return False
        print("✅ Defects table exists")
        
        # Check sample data
        cursor.execute("SELECT COUNT(*) FROM analysis")
        count = cursor.fetchone()[0]
        print(f"✅ Database has {count} sample records")
        
        conn.close()
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def check_files():
    """Check critical files exist"""
    critical_files = [
        'app_fixed.py',
        'ml_defect_detector_simple.py',
        'requirements.txt',
        'Procfile',
        'templates/index.html',
        'templates/results.html',
        'templates/reports_history.html',
        'static/style.css',
        'static/script.js'
    ]
    
    all_good = True
    for file_path in critical_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path} exists")
        else:
            print(f"❌ {file_path} missing")
            all_good = False
    
    return all_good

def check_procfile():
    """Check Procfile configuration"""
    try:
        with open('Procfile', 'r') as f:
            content = f.read().strip()
        
        if 'app_fixed:app' in content:
            print("✅ Procfile points to app_fixed:app")
            return True
        else:
            print(f"❌ Procfile incorrect: {content}")
            return False
    except Exception as e:
        print(f"❌ Procfile error: {e}")
        return False

def main():
    """Run all deployment checks"""
    print("🚀 Pre-deployment verification starting...\n")
    
    checks = [
        ("Imports", check_imports),
        ("Database", check_database),
        ("Files", check_files),
        ("Procfile", check_procfile)
    ]
    
    all_passed = True
    for name, check_func in checks:
        print(f"\n📋 Checking {name}...")
        if not check_func():
            all_passed = False
    
    print("\n" + "="*50)
    if all_passed:
        print("🎉 ALL CHECKS PASSED - READY FOR DEPLOYMENT!")
        print("\nNext steps:")
        print("1. git add .")
        print("2. git commit -m 'Ready for deployment'")
        print("3. git push origin main")
        print("4. Deploy to Railway")
        return 0
    else:
        print("❌ SOME CHECKS FAILED - FIX ISSUES BEFORE DEPLOYMENT")
        return 1

if __name__ == "__main__":
    sys.exit(main())
