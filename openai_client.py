from pathlib import Path
import google.generativeai as genai
from google.cloud import texttospeech
import os
import re

class GeminiClient:
    """
    A client for interacting with Google's Gemini API for conversational AI and text-to-speech functionalities.
    """
    def __init__(self, api_key=None):
        # Use provided API key or get from environment
        if api_key:
            genai.configure(api_key=api_key)
        else:
            # Try to get API key from environment
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
            else:
                raise ValueError("Gemini API key not provided and not found in environment variables")

        # Dynamic stable model selection (can override via GEMINI_MODEL env)
        # Single-model selection: default to gemini-2.5-flash, override with GEMINI_MODEL env
        requested = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        base_name = requested.split('/')[-1]
        try:
            raw_models = genai.list_models()
            available_models = [m.name for m in raw_models if 'generateContent' in getattr(m, 'supported_generation_methods', [])]
            available_base = {name.split('/')[-1]: name for name in available_models}
            print(f"Gemini available models (generateContent): {list(available_base.keys())}")
        except Exception as e:
            print(f"Warning: Could not list Gemini models ({e}); proceeding with requested model blindly.")
            available_base = {base_name: base_name}
        target_full_name = available_base.get(base_name)
        if not target_full_name:
            raise RuntimeError(f"Requested model '{base_name}' not available. Set GEMINI_MODEL to one of: {list(available_base.keys())}")
        self.active_model_name = base_name
        self.model = genai.GenerativeModel(target_full_name)

        # Initialize TTS client with credentials
        try:
            self.tts_client = texttospeech.TextToSpeechClient()
        except Exception as e:
            print(f"Warning: Could not initialize TTS client: {e}")
            self.tts_client = None

    def chat_with_gemini(self, prompt, context=None, locale=None):
        """Generate response using Gemini AI with optional context and locale hint"""
        try:
            system_hint = ""
            lang_name = "English"  # Default language name
            
            if locale:
                # Map locale to language name for clarity
                locale_map = {
                    'ta-IN': 'Tamil', 'hi-IN': 'Hindi', 'mr-IN': 'Marathi',
                    'gu-IN': 'Gujarati', 'te-IN': 'Telugu', 'kn-IN': 'Kannada',
                    'bn-IN': 'Bengali', 'ml-IN': 'Malayalam', 'en-US': 'English'
                }
                lang_name = locale_map.get(locale, locale)
                
                # Enhanced system instruction for strict language compliance
                system_hint = f"""CRITICAL INSTRUCTION: You MUST respond EXCLUSIVELY in {lang_name} language for VOICE OUTPUT.

STRICT RULES FOR VOICE-FRIENDLY RESPONSES:
1. Write your ENTIRE response in {lang_name} script and language ONLY
2. NEVER use English words - translate ALL terms to {lang_name}
3. NEVER use English abbreviations like "EMI", "SMS" - say the full {lang_name} equivalent
4. Do NOT use markdown formatting (* # - etc.) - this is for voice, not text
5. Do NOT use bullet points or lists - use natural conversational sentences
6. Do NOT use romanized {lang_name} - use native {lang_name} script only
7. Technical terms MUST be in {lang_name} (e.g., "installment" not "EMI")
8. Keep responses conversational and natural for speech
9. Avoid special characters, symbols, numbers in English

Example of what NOT to do: "EMI options available"
Example of what TO do: Translate fully to {lang_name} conversational speech

This is for VOICE ASSISTANT - must be speakable in {lang_name} only!

"""
            
            # Build full prompt based on whether we have context
            if context:
                if locale:
                    full_prompt = f"{system_hint}{context}\n\nUser Query: {prompt}\n\nRemember: Respond ONLY in {lang_name} language."
                else:
                    full_prompt = f"{context}\n\nUser Query: {prompt}"
            else:
                if locale:
                    full_prompt = f"{system_hint}{prompt}\n\nRemember: Respond ONLY in {lang_name} language."
                else:
                    full_prompt = prompt

            response = self.model.generate_content(full_prompt)
            response_text = (response.text or "").strip()
            
            # Log for debugging
            if locale and locale != 'en-US':
                print(f"Gemini response in {lang_name}: {response_text[:100]}...")
            
            return response_text
        except Exception as e:
            err_text = str(e)
            print(f"Error in Gemini chat ({self.active_model_name or 'none'}): {err_text}")
            if any(flag in err_text.lower() for flag in ["429", "quota"]):
                return f"Model '{self.active_model_name}' quota exceeded. Retry later or set GEMINI_MODEL=gemini-2.5-pro."
            if any(flag in err_text.lower() for flag in ["404", "not found"]):
                return f"Model '{self.active_model_name}' unavailable. Set GEMINI_MODEL=gemini-2.5-flash or GEMINI_MODEL=gemini-2.5-pro and restart."
            return "Gemini model error. Retry shortly."

    def clean_text_for_speech(self, text, language_code="en-US"):
        """Clean text to make it more voice-friendly by removing markdown and special characters"""
        # Remove markdown formatting
        text = re.sub(r'\*\*(.+?)\*\*', r'\1', text)  # Remove bold **text**
        text = re.sub(r'\*(.+?)\*', r'\1', text)      # Remove italic *text*
        text = re.sub(r'_(.+?)_', r'\1', text)        # Remove _text_
        text = re.sub(r'#+ ', '', text)               # Remove headers #
        text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', text)  # Remove links [text](url)
        
        # Remove bullet points and list markers
        text = re.sub(r'^\s*[-*•]\s+', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*\d+\.\s+', '', text, flags=re.MULTILINE)
        
        # Remove extra whitespace and newlines
        text = re.sub(r'\n+', '. ', text)
        text = re.sub(r'\s+', ' ', text)
        
        # For non-English languages, try to detect and warn about remaining English words
        if language_code != "en-US":
            # Simple check for common English words (basic detection)
            english_pattern = r'\b(the|and|is|are|was|were|in|on|at|to|for|of|with|from|by|EMI|SMS|email|phone)\b'
            english_matches = re.findall(english_pattern, text, re.IGNORECASE)
            if english_matches:
                print(f"[WARNING] Detected possible English words in {language_code} text: {set(english_matches)}")
        
        return text.strip()

    def text_to_speech_browser_fallback(self, text, language_code="en-US"):
        """
        Returns cleaned text for browser's speechSynthesis API to use.
        This is a free alternative that works without Google Cloud TTS billing.
        The actual speech synthesis will be handled by the browser.
        """
        cleaned_text = self.clean_text_for_speech(text, language_code)
        print(f"[TTS] Prepared text for browser synthesis in {language_code}")
        print(f"[TTS] Text preview: {cleaned_text[:100]}...")
        return cleaned_text

    def text_to_speech(self, text, language_code="en-US"):
        """Convert text to speech with specified language, using best available voice"""
        if not self.tts_client:
            print("TTS client not available")
            return None

        try:
            # Clean text before converting to speech
            cleaned_text = self.clean_text_for_speech(text, language_code)
            print(f"[TTS] Original text length: {len(text)}, Cleaned: {len(cleaned_text)}")
            if len(cleaned_text) < len(text) * 0.5:
                print(f"[TTS WARNING] Text was heavily cleaned, using original")
                cleaned_text = text  # Fallback if too much was removed
            # Language-specific voice configurations for better Indian language support
            language_voice_map = {
                'hi-IN': {'name': 'hi-IN-Standard-D', 'gender': texttospeech.SsmlVoiceGender.FEMALE},
                'ta-IN': {'name': 'ta-IN-Standard-A', 'gender': texttospeech.SsmlVoiceGender.FEMALE},
                'te-IN': {'name': 'te-IN-Standard-A', 'gender': texttospeech.SsmlVoiceGender.FEMALE},
                'kn-IN': {'name': 'kn-IN-Standard-A', 'gender': texttospeech.SsmlVoiceGender.FEMALE},
                'ml-IN': {'name': 'ml-IN-Standard-A', 'gender': texttospeech.SsmlVoiceGender.FEMALE},
                'gu-IN': {'name': 'gu-IN-Standard-A', 'gender': texttospeech.SsmlVoiceGender.FEMALE},
                'mr-IN': {'name': 'mr-IN-Standard-A', 'gender': texttospeech.SsmlVoiceGender.FEMALE},
                'bn-IN': {'name': 'bn-IN-Standard-A', 'gender': texttospeech.SsmlVoiceGender.FEMALE},
            }

            synthesis_input = texttospeech.SynthesisInput(text=cleaned_text)
            
            # Try to use language-specific voice configuration
            if language_code in language_voice_map:
                voice_config = language_voice_map[language_code]
                try:
                    # Try with specific voice name first
                    voice = texttospeech.VoiceSelectionParams(
                        language_code=language_code,
                        name=voice_config['name']
                    )
                    audio_config = texttospeech.AudioConfig(
                        audio_encoding=texttospeech.AudioEncoding.MP3,
                        speaking_rate=1.0,
                        pitch=0.0
                    )
                    
                    response = self.tts_client.synthesize_speech(
                        input=synthesis_input, voice=voice, audio_config=audio_config
                    )
                    
                    filename = Path(__file__).parent / "output_speech.mp3"
                    with open(str(filename), "wb") as f:
                        f.write(response.audio_content)
                    print(f"TTS successful with voice: {voice_config['name']}")
                    return str(filename)
                except Exception as voice_error:
                    print(f"Specific voice failed: {voice_error}, trying generic voice for {language_code}")
                    # Fall through to generic voice selection
            
            # Generic voice selection (fallback or for unsupported languages)
            voice = texttospeech.VoiceSelectionParams(
                language_code=language_code,
                ssml_gender=texttospeech.SsmlVoiceGender.FEMALE  # Changed from NEUTRAL to FEMALE for better availability
            )
            audio_config = texttospeech.AudioConfig(
                audio_encoding=texttospeech.AudioEncoding.MP3,
                speaking_rate=1.0,
                pitch=0.0
            )

            response = self.tts_client.synthesize_speech(
                input=synthesis_input, voice=voice, audio_config=audio_config
            )

            filename = Path(__file__).parent / "output_speech.mp3"
            with open(str(filename), "wb") as f:
                f.write(response.audio_content)
            print(f"TTS successful with generic voice for {language_code}")
            return str(filename)
        except Exception as e:
            print(f"Error in TTS for {language_code}: {e}")
            # Last resort: try English as fallback
            try:
                print(f"Attempting English fallback for text: {text[:50]}...")
                synthesis_input = texttospeech.SynthesisInput(text=text)
                voice = texttospeech.VoiceSelectionParams(
                    language_code="en-US",
                    ssml_gender=texttospeech.SsmlVoiceGender.FEMALE
                )
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.MP3
                )
                response = self.tts_client.synthesize_speech(
                    input=synthesis_input, voice=voice, audio_config=audio_config
                )
                filename = Path(__file__).parent / "output_speech.mp3"
                with open(str(filename), "wb") as f:
                    f.write(response.audio_content)
                print("TTS fallback to English successful")
                return str(filename)
            except Exception as fallback_error:
                print(f"TTS fallback also failed: {fallback_error}")
                return None

    def generate_dealership_response(self, query, bike_data=None, service_data=None, dealer_data=None, locale=None):
        """Generate intelligent dealership response using Gemini AI with language support"""
        context = f"""
You are an AI assistant for EveryLingua Motors, a motorcycle dealership.
You have access to the following information:

BIKE INVENTORY:
{bike_data if bike_data else 'No bike data available'}

SERVICE PACKAGES:
{service_data if service_data else 'No service data available'}

DEALERSHIP LOCATIONS:
{dealer_data if dealer_data else 'No dealer data available'}

Please provide helpful, accurate responses about:
- Available motorcycle models and prices
- EMI and financing options
- Test ride bookings
- Service appointments
- Dealership locations
- General motorcycle information

Be conversational, friendly, and professional. If you don't have specific information, provide general guidance and offer to connect the customer with a human representative.
"""

        return self.chat_with_gemini(query, context, locale)
