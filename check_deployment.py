#!/usr/bin/env python3
"""
Railway Deployment Status Checker
"""

import requests
import time
from datetime import datetime

def check_deployment_status():
    """Check if the app is deployed and working"""
    
    # Your Railway project URLs
    possible_urls = [
        "https://defect-production.up.railway.app",
        "https://web-production-56507d0f.up.railway.app"
    ]
    
    print("🚀 Checking Railway deployment status...")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*50)
    
    for url in possible_urls:
        try:
            print(f"🔍 Checking: {url}")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                print(f"✅ DEPLOYED SUCCESSFULLY!")
                print(f"🌐 Live URL: {url}")
                print(f"📊 Status Code: {response.status_code}")
                print(f"📝 Title: {response.text[:100]}...")
                return url
            else:
                print(f"⚠️ Response: {response.status_code}")
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Connection failed: {e}")
    
    print("\n📋 Next Steps:")
    print("1. Check Railway dashboard for deployment logs")
    print("2. Ensure GitHub repository is connected")
    print("3. Verify Procfile and requirements.txt")
    print("4. Check for any build errors")
    
    return None

if __name__ == "__main__":
    live_url = check_deployment_status()
    
    if live_url:
        print(f"\n🎉 SUCCESS! Your app is live at: {live_url}")
        print("\n🔧 Test Features:")
        print("- Upload a PDF/DOCX building report")
        print("- Check navigation between reports")
        print("- Try the sample data at /dashboard")
    else:
        print("\n⏳ Deployment may still be in progress...")
        print("Railway deployments typically take 3-5 minutes")
