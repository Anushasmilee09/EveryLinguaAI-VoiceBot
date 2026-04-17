"""
Test script to verify multilingual TTS responses
This script tests the chat API with different languages and outputs the responses
"""

import requests
import json

BASE_URL = "http://localhost:5000"

def test_language(language_code, language_name, message="hello"):
    """Test chat API with a specific language"""
    print(f"\n{'='*60}")
    print(f"Testing: {language_name} ({language_code})")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/chat",
            headers={"Content-Type": "application/json"},
            json={
                "message": message,
                "is_voice": True,
                "language": language_code
            },
            timeout=30
        )
        
        data = response.json()
        
        if data.get('success'):
            print(f"✅ Success!")
            print(f"Language: {data.get('language')}")
            print(f"Response: {data.get('response')}")
            print(f"Should Speak: {data.get('should_speak')}")
            return True
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_registration():
    """Test user registration endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: User Registration")
    print(f"{'='*60}")
    
    try:
        # Test with a unique email
        import time
        unique_email = f"test_{int(time.time())}@test.com"
        
        response = requests.post(
            f"{BASE_URL}/api/auth/register",
            headers={"Content-Type": "application/json"},
            json={
                "full_name": "Test User",
                "email": unique_email,
                "phone": "+919876543210",
                "password": "test123",
                "skip_otp": True
            },
            timeout=10
        )
        
        data = response.json()
        
        if data.get('success'):
            print(f"✅ Registration successful!")
            print(f"User: {data.get('user')}")
            print(f"Session Token: {data.get('session_token', 'N/A')[:20]}...")
            return True
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def test_login():
    """Test user login endpoint"""
    print(f"\n{'='*60}")
    print(f"Testing: User Login")
    print(f"{'='*60}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/auth/login",
            headers={"Content-Type": "application/json"},
            json={
                "email": "test@test.com",
                "password": "test123",
                "remember_me": True
            },
            timeout=10
        )
        
        data = response.json()
        
        if data.get('success'):
            print(f"✅ Login successful!")
            print(f"User: {data.get('user')}")
            print(f"Session Token: {data.get('session_token', 'N/A')[:20]}...")
            return True
        else:
            print(f"❌ Error: {data.get('error')}")
            return False
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("EVERYLINGUA AI - MULTILINGUAL TTS TEST")
    print("="*60)
    
    # Test languages
    languages = [
        ("en-US", "English"),
        ("hi-IN", "Hindi"),
        ("ta-IN", "Tamil"),
        ("te-IN", "Telugu"),
        ("kn-IN", "Kannada"),
        ("mr-IN", "Marathi"),
        ("gu-IN", "Gujarati"),
        ("bn-IN", "Bengali"),
    ]
    
    results = {}
    
    # Test each language
    for lang_code, lang_name in languages:
        results[lang_code] = test_language(lang_code, lang_name)
    
    # Test authentication
    test_registration()
    test_login()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for lang_code, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {lang_code}: {status}")
    
    print(f"\nTotal: {passed}/{total} passed")
    
    if passed == total:
        print("\n🎉 All multilingual tests passed!")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed")

if __name__ == "__main__":
    main()