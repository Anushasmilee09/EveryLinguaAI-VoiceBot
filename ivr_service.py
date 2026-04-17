"""
IVR (Interactive Voice Response) Service for EveryLingua AI
Provides phone-based customer support with multilingual voice menus via Twilio TwiML.

Flow:
  Welcome → Language Select → Main Menu → [Bookings | Services | Hours | Agent]
"""

import os
import sqlite3
from datetime import datetime


# ── IVR Language Configs ─────────────────────────────────────────────────────

IVR_LANGUAGES = {
    '1': {'code': 'en', 'name': 'English', 'voice': 'alice'},
    '2': {'code': 'hi', 'name': 'Hindi', 'voice': 'alice'},
    '3': {'code': 'ta', 'name': 'Tamil', 'voice': 'alice'},
    '4': {'code': 'te', 'name': 'Telugu', 'voice': 'alice'},
    '5': {'code': 'kn', 'name': 'Kannada', 'voice': 'alice'},
    '6': {'code': 'mr', 'name': 'Marathi', 'voice': 'alice'},
}

# ── Greeting / Menu Strings (per language) ───────────────────────────────────

GREETINGS = {
    'en': "Welcome to EveryLingua Motors! Your trusted motorcycle partner.",
    'hi': "एवरीलिंगुआ मोटर्स में आपका स्वागत है! आपका विश्वसनीय मोटरसाइकिल भागीदार।",
    'ta': "எவரிலிங்குவா மோட்டார்ஸ் வரவேற்கிறோம்! உங்கள் நம்பகமான மோட்டார் சைக்கிள் கூட்டாளி.",
    'te': "ఎవరీలింగ్వా మోటార్స్‌కి స్వాగతం! మీ నమ్మకమైన మోటార్‌సైకిల్ భాగస్వామి.",
    'kn': "ಎವೆರಿಲಿಂಗ್ವಾ ಮೋಟಾರ್ಸ್‌ಗೆ ಸ್ವಾಗತ! ನಿಮ್ಮ ನಂಬಿಕೆಯ ಮೋಟರ್‌ಸೈಕಲ್ ಪಾಲುದಾರ.",
    'mr': "एव्हरीलिंग्वा मोटर्समध्ये आपले स्वागत आहे! आपला विश्वासू मोटरसायकल भागीदार.",
}

MAIN_MENU = {
    'en': "Press 1 for Booking Status. Press 2 for Service Packages. Press 3 for Dealership Hours. Press 4 to speak with an Agent. Press 0 to repeat this menu.",
    'hi': "बुकिंग स्थिति के लिए 1 दबाएं। सर्विस पैकेज के लिए 2 दबाएं। डीलरशिप समय के लिए 3 दबाएं। एजेंट से बात करने के लिए 4 दबाएं। मेनू दोहराने के लिए 0 दबाएं।",
    'ta': "புக்கிங் நிலைக்கு 1 அழுத்தவும். சேவை தொகுப்புகளுக்கு 2. டீலர்ஷிப் நேரங்களுக்கு 3. முகவருடன் பேச 4. மீண்டும் கேட்க 0.",
    'te': "బుకింగ్ స్థితి కోసం 1 నొక్కండి. సేవా ప్యాకేజీలకు 2. డీలర్‌షిప్ గంటలకు 3. ఏజెంట్‌తో మాట్లాడటానికి 4. మెనూ మళ్ళీ వినడానికి 0.",
    'kn': "ಬುಕಿಂಗ್ ಸ್ಥಿತಿಗೆ 1 ಒತ್ತಿ. ಸೇವಾ ಪ್ಯಾಕೇಜ್‌ಗಳಿಗೆ 2. ಡೀಲರ್‌ಶಿಪ್ ಸಮಯಕ್ಕೆ 3. ಏಜೆಂಟ್‌ನೊಂದಿಗೆ ಮಾತನಾಡಲು 4. ಮೆನು ಮರುಕೇಳಲು 0.",
    'mr': "बुकिंग स्थितीसाठी 1 दाबा. सर्व्हिस पॅकेजसाठी 2. डीलरशिप वेळेसाठी 3. एजंटशी बोलण्यासाठी 4. मेनू पुन्हा ऐकण्यासाठी 0.",
}

BOOKING_PROMPT = {
    'en': "Please enter your booking ID followed by the hash key.",
    'hi': "कृपया अपनी बुकिंग आईडी दर्ज करें और हैश की दबाएं।",
    'ta': "உங்கள் புக்கிங் ஐடியை உள்ளிட்டு ஹாஷ் கீ அழுத்தவும்.",
    'te': "దయచేసి మీ బుకింగ్ ఐడీ నమోదు చేసి హాష్ కీ నొక్కండి.",
    'kn': "ದಯವಿಟ್ಟು ನಿಮ್ಮ ಬುಕಿಂಗ್ ಐಡಿ ನಮೂದಿಸಿ ಮತ್ತು ಹ್ಯಾಶ್ ಕೀ ಒತ್ತಿ.",
    'mr': "कृपया आपला बुकिंग आयडी प्रविष्ट करा आणि हॅश की दाबा.",
}

# ── Service Packages Info ────────────────────────────────────────────────────

SERVICE_INFO = {
    'en': (
        "We offer 3 service packages. "
        "Package 1: Basic Service at 999 rupees. Includes oil change, chain lubrication, and basic inspection. "
        "Package 2: Standard Service at 1999 rupees. Includes everything in Basic plus brake inspection, air filter cleaning, and spark plug check. "
        "Package 3: Premium Service at 3499 rupees. Full vehicle inspection, all fluids replacement, chain and sprocket service, and free wash."
    ),
    'hi': (
        "हम 3 सर्विस पैकेज प्रदान करते हैं। "
        "पैकेज 1: बेसिक सर्विस 999 रुपये। ऑयल चेंज, चेन लुब्रिकेशन और बेसिक इंस्पेक्शन। "
        "पैकेज 2: स्टैंडर्ड सर्विस 1999 रुपये। बेसिक के सभी और ब्रेक इंस्पेक्शन, एयर फिल्टर क्लीनिंग। "
        "पैकेज 3: प्रीमियम सर्विस 3499 रुपये। पूर्ण वाहन इंस्पेक्शन और सभी फ्लूइड्स रिप्लेसमेंट।"
    ),
}

# ── Dealership Hours ─────────────────────────────────────────────────────────

HOURS_INFO = {
    'en': (
        "Our dealership hours are: "
        "Monday to Saturday, 9 AM to 7 PM. "
        "Sunday, 10 AM to 4 PM. "
        "Service center is open Monday to Saturday, 8 AM to 6 PM."
    ),
    'hi': (
        "हमारी डीलरशिप का समय: "
        "सोमवार से शनिवार, सुबह 9 से शाम 7 बजे। "
        "रविवार, सुबह 10 से शाम 4 बजे। "
        "सर्विस सेंटर सोमवार से शनिवार, सुबह 8 से शाम 6 बजे।"
    ),
}


def _get_text(texts_dict, lang):
    """Get text for the given language, falling back to English."""
    return texts_dict.get(lang, texts_dict.get('en', ''))


# ── TwiML Builders ───────────────────────────────────────────────────────────
# These return plain XML strings (no dependency on twilio SDK).

def _twiml(body: str) -> str:
    """Wrap body in a TwiML Response envelope."""
    return f'<?xml version="1.0" encoding="UTF-8"?><Response>{body}</Response>'


def _say(text: str, lang: str = 'en', voice: str = 'alice') -> str:
    """Build a <Say> verb."""
    lang_map = {
        'en': 'en-IN', 'hi': 'hi-IN', 'ta': 'ta-IN', 'te': 'te-IN',
        'kn': 'kn-IN', 'mr': 'mr-IN', 'gu': 'gu-IN', 'bn': 'bn-IN',
    }
    bcp_lang = lang_map.get(lang, 'en-IN')
    return f'<Say voice="{voice}" language="{bcp_lang}">{text}</Say>'


def _gather(action: str, body: str, num_digits: int = 1, timeout: int = 5, finish_on_key: str = '') -> str:
    """Build a <Gather> verb wrapping body."""
    fok = f' finishOnKey="{finish_on_key}"' if finish_on_key else ''
    return (
        f'<Gather numDigits="{num_digits}" action="{action}" timeout="{timeout}"{fok}>'
        f'{body}</Gather>'
    )


# ── Webhook Handlers ─────────────────────────────────────────────────────────

def handle_welcome() -> str:
    """
    /api/ivr/welcome  – Initial greeting + language selection.
    """
    prompt = (
        "Welcome to EveryLingua Motors. "
        "Press 1 for English. "
        "Press 2 for Hindi. "
        "Press 3 for Tamil. "
        "Press 4 for Telugu. "
        "Press 5 for Kannada. "
        "Press 6 for Marathi."
    )
    body = _gather('/api/ivr/menu', _say(prompt, 'en'), num_digits=1, timeout=8)
    # If no input, replay
    body += '<Redirect>/api/ivr/welcome</Redirect>'
    return _twiml(body)


def handle_menu(digits: str = '1') -> str:
    """
    /api/ivr/menu  – Main IVR menu after language selection.
    """
    lang_cfg = IVR_LANGUAGES.get(digits, IVR_LANGUAGES['1'])
    lang = lang_cfg['code']
    voice = lang_cfg['voice']

    greeting = _get_text(GREETINGS, lang)
    menu = _get_text(MAIN_MENU, lang)

    body = _say(greeting, lang, voice)
    body += _gather(
        f'/api/ivr/route?lang={lang}',
        _say(menu, lang, voice),
        num_digits=1, timeout=8
    )
    body += f'<Redirect>/api/ivr/menu?Digits={digits}</Redirect>'
    return _twiml(body)


def handle_route(digits: str, lang: str = 'en') -> str:
    """
    /api/ivr/route  – Route user's menu choice.
    """
    if digits == '1':
        return handle_booking_prompt(lang)
    elif digits == '2':
        return handle_services(lang)
    elif digits == '3':
        return handle_hours(lang)
    elif digits == '4':
        return handle_agent(lang)
    elif digits == '0':
        # Find the original language digit for re-entering the menu
        lang_digit = '1'
        for d, cfg in IVR_LANGUAGES.items():
            if cfg['code'] == lang:
                lang_digit = d
                break
        return handle_menu(lang_digit)
    else:
        body = _say("Invalid option. Please try again.", lang)
        body += f'<Redirect>/api/ivr/menu?Digits=1</Redirect>'
        return _twiml(body)


def handle_booking_prompt(lang: str = 'en') -> str:
    """
    /api/ivr/bookings  – Ask for booking ID.
    """
    prompt = _get_text(BOOKING_PROMPT, lang)
    body = _gather(
        f'/api/ivr/booking-status?lang={lang}',
        _say(prompt, lang),
        num_digits=10, timeout=10, finish_on_key='#'
    )
    body += _say("We did not receive your booking ID. Returning to main menu.", lang)
    # Redirect to menu
    lang_digit = '1'
    for d, cfg in IVR_LANGUAGES.items():
        if cfg['code'] == lang:
            lang_digit = d
            break
    body += f'<Redirect>/api/ivr/menu?Digits={lang_digit}</Redirect>'
    return _twiml(body)


def handle_booking_status(digits: str, lang: str = 'en') -> str:
    """
    /api/ivr/booking-status  – Look up booking by ID and read status.
    """
    booking = _lookup_booking(digits)

    if booking:
        status = booking.get('status', 'unknown').replace('_', ' ')
        bike = booking.get('bike_model', 'your motorcycle')
        btype = 'test ride' if booking.get('type') == 'test_ride' else 'service'
        date = booking.get('date', '')

        if lang == 'en':
            msg = f"Booking {digits} found. Type: {btype}. Bike: {bike}. Date: {date}. Status: {status}."
        elif lang == 'hi':
            msg = f"बुकिंग {digits} मिली। प्रकार: {btype}। बाइक: {bike}। तारीख: {date}। स्थिति: {status}।"
        else:
            msg = f"Booking {digits}: {btype}, {bike}, {date}, Status: {status}."
    else:
        if lang == 'en':
            msg = f"Sorry, no booking found with ID {digits}. Please check your booking ID and try again."
        elif lang == 'hi':
            msg = f"क्षमा करें, बुकिंग आईडी {digits} से कोई बुकिंग नहीं मिली।"
        else:
            msg = f"Booking {digits} not found."

    body = _say(msg, lang)
    # Return to menu
    lang_digit = '1'
    for d, cfg in IVR_LANGUAGES.items():
        if cfg['code'] == lang:
            lang_digit = d
            break
    body += f'<Pause length="1"/>'
    body += f'<Redirect>/api/ivr/menu?Digits={lang_digit}</Redirect>'
    return _twiml(body)


def handle_services(lang: str = 'en') -> str:
    """
    /api/ivr/services  – Read service packages.
    """
    info = _get_text(SERVICE_INFO, lang)
    body = _say(info, lang)
    body += '<Pause length="1"/>'
    lang_digit = '1'
    for d, cfg in IVR_LANGUAGES.items():
        if cfg['code'] == lang:
            lang_digit = d
            break
    body += f'<Redirect>/api/ivr/menu?Digits={lang_digit}</Redirect>'
    return _twiml(body)


def handle_hours(lang: str = 'en') -> str:
    """
    /api/ivr/hours  – Read dealership hours.
    """
    info = _get_text(HOURS_INFO, lang)
    body = _say(info, lang)
    body += '<Pause length="1"/>'
    lang_digit = '1'
    for d, cfg in IVR_LANGUAGES.items():
        if cfg['code'] == lang:
            lang_digit = d
            break
    body += f'<Redirect>/api/ivr/menu?Digits={lang_digit}</Redirect>'
    return _twiml(body)


def handle_agent(lang: str = 'en') -> str:
    """
    /api/ivr/agent  – Transfer to human agent.
    """
    agent_number = os.environ.get('IVR_AGENT_NUMBER', '+919876543210')

    if lang == 'en':
        msg = "Connecting you to a customer support agent. Please hold."
    elif lang == 'hi':
        msg = "आपको कस्टमर सपोर्ट एजेंट से जोड़ रहे हैं। कृपया प्रतीक्षा करें।"
    else:
        msg = "Connecting you to an agent. Please hold."

    body = _say(msg, lang)
    body += f'<Dial timeout="30" callerId="{os.environ.get("TWILIO_PHONE_NUMBER", "+19787092329")}">{agent_number}</Dial>'
    # If agent doesn't answer
    body += _say("Sorry, no agent is available right now. Please try again later or visit our dealership.", lang)
    body += '<Hangup/>'
    return _twiml(body)


# ── Database Lookup ──────────────────────────────────────────────────────────

def _lookup_booking(booking_id: str) -> dict:
    """Look up a booking from the CRM database."""
    db_path = os.path.join(os.path.dirname(__file__), 'dealership_crm.db')
    if not os.path.exists(db_path):
        return None
    try:
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        # Try exact ID match
        cursor.execute("SELECT * FROM bookings WHERE id = ?", (booking_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None
    except Exception:
        return None

