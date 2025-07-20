#!/usr/bin/env python3
"""
UnAI Test Script
Basic functionality tests for the AI detection app
"""

import os
import sys
import requests
import tempfile
from PIL import Image
import numpy as np
import io

def create_test_image():
    """Create a simple test image"""
    # Create a simple test image (100x100 pixels)
    img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
    img = Image.fromarray(img_array)
    
    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)
    
    return img_bytes

def test_health_endpoint():
    """Test the health check endpoint"""
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=5)
        if response.status_code == 200:
            data = response.json()
            print("✅ Health check passed:", data.get('message', 'OK'))
            return True
        else:
            print(f"❌ Health check failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check error: {e}")
        return False

def test_analyze_endpoint():
    """Test the analyze endpoint with a sample image"""
    try:
        # Create test image
        img_bytes = create_test_image()
        
        # Prepare file for upload
        files = {
            'file': ('test_image.png', img_bytes, 'image/png')
        }
        
        # Send request
        response = requests.post(
            'http://localhost:5000/api/analyze', 
            files=files, 
            timeout=30
        )
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Analysis endpoint working")
            print(f"   File type: {data.get('file_type', 'unknown')}")
            print(f"   AI Generated: {data.get('is_ai_generated', 'unknown')}")
            print(f"   Confidence: {data.get('confidence', 0):.1f}%")
            return True
        else:
            print(f"❌ Analysis failed with status: {response.status_code}")
            print(f"   Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Analysis test error: {e}")
        return False

def test_web_interface():
    """Test if the web interface is accessible"""
    try:
        response = requests.get('http://localhost:5000/', timeout=5)
        if response.status_code == 200:
            if 'UnAI' in response.text:
                print("✅ Web interface accessible")
                return True
            else:
                print("❌ Web interface returned unexpected content")
                return False
        else:
            print(f"❌ Web interface failed with status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web interface test error: {e}")
        return False

def main():
    print("🧪 UnAI Application Tests")
    print("=" * 30)
    
    tests = [
        ("Health Check", test_health_endpoint),
        ("Web Interface", test_web_interface),
        ("Analysis Endpoint", test_analyze_endpoint),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🔬 Running {test_name} test...")
        if test_func():
            passed += 1
        else:
            print(f"   Test failed: {test_name}")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! UnAI is working correctly.")
        return 0
    else:
        print("⚠️ Some tests failed. Please check the application.")
        return 1

if __name__ == '__main__':
    # Check if server is running
    print("Checking if UnAI server is running on localhost:5000...")
    try:
        response = requests.get('http://localhost:5000/api/health', timeout=2)
        print("✅ Server is running")
    except:
        print("❌ Server is not running. Please start it first:")
        print("   python app.py")
        print("   or")
        print("   python run.py")
        sys.exit(1)
    
    sys.exit(main())