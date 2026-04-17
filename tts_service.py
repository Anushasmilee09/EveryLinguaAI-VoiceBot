"""
Text-to-Speech Service for EveryLingua AI
Generates MP3 audio files for multilingual speech synthesis
"""

import os
import hashlib
import time
from pathlib import Path
from gtts import gTTS

# Create output folder for TTS audio files
TTS_OUTPUT_DIR = Path("tts_output")
TTS_OUTPUT_DIR.mkdir(exist_ok=True)

# Language code mapping for gTTS
# gTTS uses ISO 639-1 codes, we need to map from BCP-47 locale codes
LANGUAGE_MAP = {
    # Indian Languages
    'en-IN': 'en', 'hi-IN': 'hi', 'ta-IN': 'ta', 'te-IN': 'te',
    'kn-IN': 'kn', 'mr-IN': 'mr', 'gu-IN': 'gu', 'bn-IN': 'bn',
    'ml-IN': 'ml', 'pa-IN': 'pa', 'ur-IN': 'ur', 'or-IN': 'or',
    'as-IN': 'as', 'ne-NP': 'ne', 'si-LK': 'si',
    # English Variants
    'en-US': 'en', 'en-GB': 'en', 'en-AU': 'en',
    # European Languages
    'es-ES': 'es', 'fr-FR': 'fr', 'de-DE': 'de', 'it-IT': 'it',
    'pt-PT': 'pt', 'pt-BR': 'pt', 'ru-RU': 'ru', 'pl-PL': 'pl',
    'nl-NL': 'nl', 'sv-SE': 'sv', 'da-DK': 'da', 'fi-FI': 'fi',
    'el-GR': 'el', 'cs-CZ': 'cs', 'ro-RO': 'ro', 'hu-HU': 'hu',
    'uk-UA': 'uk', 'tr-TR': 'tr', 'no-NO': 'no',
    # Asian Languages
    'zh-CN': 'zh-CN', 'zh-TW': 'zh-TW', 'ja-JP': 'ja', 'ko-KR': 'ko',
    'th-TH': 'th', 'vi-VN': 'vi', 'id-ID': 'id', 'ms-MY': 'ms',
    'fil-PH': 'tl', 'my-MM': 'my', 'km-KH': 'km',
    # Middle Eastern / African
    'ar-SA': 'ar', 'he-IL': 'iw', 'fa-IR': 'fa', 'sw-KE': 'sw',
    'af-ZA': 'af', 'am-ET': 'am',
    # Short code fallbacks
    'en': 'en', 'hi': 'hi', 'ta': 'ta', 'te': 'te', 'kn': 'kn',
    'mr': 'mr', 'gu': 'gu', 'bn': 'bn', 'ml': 'ml', 'pa': 'pa',
    'ur': 'ur', 'or': 'or', 'as': 'as', 'ne': 'ne',
    'es': 'es', 'fr': 'fr', 'de': 'de', 'it': 'it', 'pt': 'pt',
    'ru': 'ru', 'zh': 'zh-CN', 'ja': 'ja', 'ko': 'ko', 'ar': 'ar',
    'th': 'th', 'vi': 'vi', 'id': 'id', 'ms': 'ms', 'tr': 'tr',
}

# TLD (Top Level Domain) for regional accent
TLD_MAP = {
    # Indian accents
    'en-IN': 'co.in', 'hi-IN': 'co.in', 'ta-IN': 'co.in', 'te-IN': 'co.in',
    'kn-IN': 'co.in', 'mr-IN': 'co.in', 'gu-IN': 'co.in', 'bn-IN': 'co.in',
    'ml-IN': 'co.in', 'pa-IN': 'co.in', 'ur-IN': 'co.in', 'or-IN': 'co.in',
    'as-IN': 'co.in', 'ne-NP': 'co.in',
    # Regional accents
    'en-US': 'com', 'en-GB': 'co.uk', 'en-AU': 'com.au',
    'fr-FR': 'fr', 'de-DE': 'de', 'es-ES': 'es', 'pt-BR': 'com.br',
    'pt-PT': 'pt', 'it-IT': 'it', 'ru-RU': 'ru', 'ja-JP': 'co.jp',
    'ko-KR': 'co.kr',
}


def get_gtts_lang(language_code: str) -> str:
    """Convert BCP-47 locale code to gTTS language code"""
    return LANGUAGE_MAP.get(language_code, language_code.split('-')[0])


def get_gtts_tld(language_code: str) -> str:
    """Get TLD for regional accent"""
    return TLD_MAP.get(language_code, 'com')


def generate_tts_audio(text: str, language: str = 'en-US', filename: str = None) -> dict:
    """
    Generate TTS audio file for the given text
    
    Args:
        text: The text to convert to speech
        language: BCP-47 language code (e.g., 'hi-IN', 'ta-IN')
        filename: Optional custom filename (without extension)
        
    Returns:
        dict with success status, file path, and metadata
    """
    try:
        if not text or not text.strip():
            return {
                'success': False,
                'error': 'No text provided'
            }
        
        # Get gTTS language code
        gtts_lang = get_gtts_lang(language)
        gtts_tld = get_gtts_tld(language)
        
        # Generate filename if not provided
        if not filename:
            # Create hash-based filename for caching
            text_hash = hashlib.md5(f"{text}_{language}".encode()).hexdigest()[:12]
            timestamp = int(time.time())
            filename = f"tts_{gtts_lang}_{timestamp}_{text_hash}"
        
        # Full path for the output file
        output_path = TTS_OUTPUT_DIR / f"{filename}.mp3"
        
        # Generate TTS audio
        print(f"Generating TTS for language: {gtts_lang} (from {language})")
        print(f"Text: {text[:100]}...")
        
        tts = gTTS(text=text, lang=gtts_lang, tld=gtts_tld, slow=False)
        tts.save(str(output_path))
        
        # Get file size
        file_size = output_path.stat().st_size
        
        return {
            'success': True,
            'file_path': str(output_path),
            'filename': f"{filename}.mp3",
            'language': language,
            'gtts_lang': gtts_lang,
            'file_size': file_size,
            'text_length': len(text)
        }
        
    except Exception as e:
        print(f"TTS generation error: {e}")
        return {
            'success': False,
            'error': str(e),
            'language': language
        }


def generate_chat_tts(text: str, language: str = 'en-US', chat_id: str = None) -> dict:
    """
    Generate TTS audio for chat response
    Uses a chat-specific filename format
    """
    if chat_id:
        filename = f"chat_{chat_id}_{language.split('-')[0]}"
    else:
        timestamp = int(time.time() * 1000)
        filename = f"chat_{timestamp}_{language.split('-')[0]}"
    
    return generate_tts_audio(text, language, filename)


def list_tts_files() -> list:
    """List all generated TTS files"""
    files = []
    for f in TTS_OUTPUT_DIR.glob("*.mp3"):
        files.append({
            'filename': f.name,
            'path': str(f),
            'size': f.stat().st_size,
            'created': f.stat().st_ctime
        })
    return sorted(files, key=lambda x: x['created'], reverse=True)


def cleanup_old_files(max_age_hours: int = 24, max_files: int = 100):
    """Clean up old TTS files"""
    import time
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    
    files = list(TTS_OUTPUT_DIR.glob("*.mp3"))
    
    # Sort by creation time (oldest first)
    files.sort(key=lambda f: f.stat().st_ctime)
    
    deleted = 0
    
    # Delete files older than max_age
    for f in files:
        age = current_time - f.stat().st_ctime
        if age > max_age_seconds:
            f.unlink()
            deleted += 1
    
    # If still too many files, delete oldest ones
    files = list(TTS_OUTPUT_DIR.glob("*.mp3"))
    if len(files) > max_files:
        files.sort(key=lambda f: f.stat().st_ctime)
        for f in files[:len(files) - max_files]:
            f.unlink()
            deleted += 1
    
    return deleted


# Test function
if __name__ == "__main__":
    # Test TTS generation for all supported languages
    test_texts = {
        'en-US': "Hello! Welcome to EveryLingua Motors. How can I help you today?",
        'hi-IN': "नमस्ते! एवरीलिंगुआ मोटर्स में आपका स्वागत है। आज मैं आपकी कैसे मदद कर सकता हूं?",
        'ta-IN': "வணக்கம்! எவரிலிங்குவா மோட்டார்ஸ் வரவேற்கிறோம். நான் எப்படி உதவ முடியும்?",
        'te-IN': "నమస్కారం! ఎవరీలింగ్వా మోటార్స్‌కి స్వాగతం. నేను మీకు ఎలా సహాయం చేయగలను?",
        'kn-IN': "ನಮಸ್ಕಾರ! ಎವೆರಿಲಿಂಗ್ವಾ ಮೋಟಾರ್ಸ್‌ಗೆ ಸ್ವಾಗತ. ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
        'mr-IN': "नमस्कार! एव्हरीलिंग्वा मोटर्समध्ये आपले स्वागत आहे. मी तुम्हाला कशी मदत करू शकतो?",
        'gu-IN': "નમસ્તે! એવરીલિંગ્વા મોટર્સમાં આપનું સ્વાગત છે. હું તમને કેવી રીતે મદદ કરી શકું?",
        'bn-IN': "নমস্কার! এভরি লিঙ্গুয়া মোটরসে স্বাগতম। আমি কীভাবে আপনাকে সাহায্য করতে পারি?",
    }
    
    print("Testing TTS generation for all languages...")
    print("=" * 60)
    
    for lang, text in test_texts.items():
        print(f"\nTesting {lang}...")
        result = generate_tts_audio(text, lang)
        if result['success']:
            print(f"  ✅ Success: {result['filename']} ({result['file_size']} bytes)")
        else:
            print(f"  ❌ Error: {result['error']}")
    
    print("\n" + "=" * 60)
    print("Generated files:")
    for f in list_tts_files():
        print(f"  - {f['filename']} ({f['size']} bytes)")