"""
Test script to verify multilingual TTS with actual MP3 audio file generation
This script tests the TTS API with different languages and saves the audio files
"""

import requests
import json
import os
from pathlib import Path

BASE_URL = "http://localhost:5000"
OUTPUT_DIR = Path("tts_output")

def test_tts_language(language_code, language_name, text=None):
    """Test TTS API with a specific language and generate MP3 file"""
    print(f"\n{'='*60}")
    print(f"Testing TTS: {language_name} ({language_code})")
    print(f"{'='*60}")
    
    # Default test texts for each language
    test_texts = {
        'hi-IN': "नमस्ते! एवरीलिंगुआ मोटर्स में आपका स्वागत है। आज मैं आपकी कैसे मदद कर सकता हूं?",
        'ta-IN': "வணக்கம்! எவரிலிங்குவா மோட்டார்ஸ் வரவேற்கிறோம். நான் எப்படி உதவ முடியும்?",
        'te-IN': "నమస్కారం! ఎవరీలింగ్వా మోటార్స్‌కి స్వాగతం. నేను మీకు ఎలా సహాయం చేయగలను?",
        'kn-IN': "ನಮಸ್ಕಾರ! ಎವೆರಿಲಿಂಗ್ವಾ ಮೋಟಾರ್ಸ್‌ಗೆ ಸ್ವಾಗತ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
        'mr-IN': "नमस्कार! एव्हरीलिंग्वा मोटर्समध्ये आपले स्वागत आहे. मी तुम्हाला कशी मदत करू शकतो?",
        'gu-IN': "નમસ્તે! એવરીલિંગ્વા મોટર્સમાં આપનું સ્વાગત છે. હું તમને કેવી રીતે મદદ કરી શકું?",
        'bn-IN': "নমস্কার! এভরি লিঙ্গুয়া মোটরসে স্বাগতম। আমি কীভাবে আপনাকে সাহায্য করতে পারি?",
    }
    
    if text is None:
        text = test_texts.get(language_code, f"Hello from EveryLingua Motors in {language_name}")
    
    print(f"Text: {text[:80]}...")
    
    try:
        # Call TTS API
        response = requests.post(
            f"{BASE_URL}/api/tts/generate",
            headers={"Content-Type": "application/json"},
            json={
                "text": text,
                "language": language_code
            },
            timeout=60
        )
        
        data = response.json()
        
        if data.get('success'):
            print(f"✅ TTS generated successfully!")
            print(f"   File URL: {data.get('file_url')}")
            print(f"   Filename: {data.get('filename')}")
            print(f"   File Size: {data.get('file_size')} bytes")
            
            # Download the audio file
            audio_url = f"{BASE_URL}{data.get('file_url')}"
            audio_response = requests.get(audio_url, timeout=30)
            
            if audio_response.status_code == 200:
                # Save to local file with language-specific name
                local_filename = f"tts_test_{language_code.replace('-', '_')}.mp3"
                local_path = OUTPUT_DIR / local_filename
                
                with open(local_path, 'wb') as f:
                    f.write(audio_response.content)
                
                print(f"   ✅ Audio saved to: {local_path}")
                print(f"   Audio size: {len(audio_response.content)} bytes")
                return True, local_path
            else:
                print(f"   ❌ Failed to download audio: HTTP {audio_response.status_code}")
                return False, None
        else:
            print(f"❌ TTS Error: {data.get('error')}")
            return False, None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, None


def test_chat_with_tts(language_code, language_name, message="hello"):
    """Test chat API followed by TTS generation"""
    print(f"\n{'='*60}")
    print(f"Testing Chat + TTS: {language_name} ({language_code})")
    print(f"{'='*60}")
    
    try:
        # First get chat response
        chat_response = requests.post(
            f"{BASE_URL}/api/chat",
            headers={"Content-Type": "application/json"},
            json={
                "message": message,
                "is_voice": True,
                "language": language_code
            },
            timeout=30
        )
        
        chat_data = chat_response.json()
        
        if chat_data.get('success'):
            response_text = chat_data.get('response', '')
            print(f"Chat Response ({language_code}): {response_text[:100]}...")
            
            # Now generate TTS for the response
            tts_response = requests.post(
                f"{BASE_URL}/api/tts/chat",
                headers={"Content-Type": "application/json"},
                json={
                    "text": response_text,
                    "language": language_code,
                    "chat_id": f"test_{language_code}"
                },
                timeout=60
            )
            
            tts_data = tts_response.json()
            
            if tts_data.get('success'):
                print(f"✅ Chat TTS generated!")
                print(f"   Audio URL: {tts_data.get('audio_url')}")
                print(f"   File Size: {tts_data.get('file_size')} bytes")
                
                # Download the audio file
                audio_url = f"{BASE_URL}{tts_data.get('audio_url')}"
                audio_response = requests.get(audio_url, timeout=30)
                
                if audio_response.status_code == 200:
                    local_filename = f"chat_tts_{language_code.replace('-', '_')}.mp3"
                    local_path = OUTPUT_DIR / local_filename
                    
                    with open(local_path, 'wb') as f:
                        f.write(audio_response.content)
                    
                    print(f"   ✅ Audio saved to: {local_path}")
                    return True, local_path
                
            else:
                print(f"❌ TTS Error: {tts_data.get('error')}")
                return False, None
        else:
            print(f"❌ Chat Error: {chat_data.get('error')}")
            return False, None
            
    except Exception as e:
        print(f"❌ Exception: {e}")
        return False, None


def main():
    print("\n" + "="*60)
    print("EVERYLINGUA AI - MULTILINGUAL TTS AUDIO FILE TEST")
    print("="*60)
    
    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)
    print(f"\nOutput directory: {OUTPUT_DIR.absolute()}")
    
    # Test languages (excluding English as per user request)
    languages = [
        ("hi-IN", "Hindi"),
        ("ta-IN", "Tamil"),
        ("te-IN", "Telugu"),
        ("kn-IN", "Kannada"),
        ("mr-IN", "Marathi"),
        ("gu-IN", "Gujarati"),
        ("bn-IN", "Bengali"),
    ]
    
    tts_results = {}
    chat_tts_results = {}
    
    # Test TTS generation for each language
    print("\n" + "="*60)
    print("PART 1: DIRECT TTS GENERATION")
    print("="*60)
    
    for lang_code, lang_name in languages:
        success, filepath = test_tts_language(lang_code, lang_name)
        tts_results[lang_code] = {'success': success, 'filepath': filepath}
    
    # Test Chat + TTS for each language
    print("\n" + "="*60)
    print("PART 2: CHAT + TTS GENERATION")
    print("="*60)
    
    for lang_code, lang_name in languages:
        success, filepath = test_chat_with_tts(lang_code, lang_name)
        chat_tts_results[lang_code] = {'success': success, 'filepath': filepath}
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    print("\nDirect TTS Generation:")
    tts_passed = sum(1 for v in tts_results.values() if v['success'])
    for lang_code, result in tts_results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        filepath = result.get('filepath', 'N/A')
        print(f"  {lang_code}: {status} - {filepath}")
    
    print(f"\nTTS Total: {tts_passed}/{len(tts_results)} passed")
    
    print("\nChat + TTS Generation:")
    chat_passed = sum(1 for v in chat_tts_results.values() if v['success'])
    for lang_code, result in chat_tts_results.items():
        status = "✅ PASS" if result['success'] else "❌ FAIL"
        filepath = result.get('filepath', 'N/A')
        print(f"  {lang_code}: {status} - {filepath}")
    
    print(f"\nChat TTS Total: {chat_passed}/{len(chat_tts_results)} passed")
    
    # List all generated files
    print("\n" + "="*60)
    print("GENERATED MP3 FILES")
    print("="*60)
    
    mp3_files = list(OUTPUT_DIR.glob("*.mp3"))
    if mp3_files:
        total_size = 0
        for f in sorted(mp3_files):
            size = f.stat().st_size
            total_size += size
            print(f"  📁 {f.name} ({size:,} bytes)")
        print(f"\nTotal: {len(mp3_files)} files, {total_size:,} bytes")
    else:
        print("  No MP3 files found")
    
    # Overall result
    total_passed = tts_passed + chat_passed
    total_tests = len(tts_results) + len(chat_tts_results)
    
    if total_passed == total_tests:
        print("\n🎉 All multilingual TTS tests passed!")
    else:
        print(f"\n⚠️ {total_tests - total_passed} test(s) failed")


if __name__ == "__main__":
    main()