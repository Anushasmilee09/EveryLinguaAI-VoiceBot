# 🏍️ EveryLingua AI - Multilingual Motorcycle Dealership Voice Assistant

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-3.0-green.svg)](https://flask.palletsprojects.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A complete AI-powered voice assistant for motorcycle dealerships with **multilingual support** for 8 Indian languages, featuring test ride booking, service scheduling, dealer locator, and 24/7 customer support.

![EveryLingua AI](https://img.shields.io/badge/EveryLingua-AI%20Assistant-667eea?style=for-the-badge)

---

## ✨ Features

### 🎙️ Voice & Language
- **8 Indian Languages**: English, Hindi, Marathi, Gujarati, Tamil, Telugu, Kannada, Bengali
- **Voice Recognition**: Browser-based speech recognition
- **Text-to-Speech**: Native TTS with language-specific voices
- **Real-time Translation**: Seamless multilingual conversations

### 🏍️ Dealership Services
- **Bike Catalog**: Browse 15+ motorcycle models with specs and pricing
- **Test Ride Booking**: Schedule test rides at any of 20 dealerships
- **Service Booking**: Book maintenance and repair appointments
- **EMI Calculator**: Calculate monthly payments with flexible options

### 📍 Dealer Network
- **20 Dealerships** across India (Mumbai, Delhi NCR, Bangalore, Chennai, Hyderabad, etc.)
- **Interactive Map**: Find nearest dealers with distance calculation
- **Real-time Availability**: Check service slot availability

### 👤 User Management
- **Secure Authentication**: Login/signup with session management
- **OTP Verification**: Email/SMS based verification
- **Remember Me**: 2-day session persistence
- **Profile Management**: User dashboard and preferences

### 🤖 AI Features
- **Gemini AI Integration**: Intelligent conversational responses
- **Human Agent Fallback**: Escalate complex queries to support
- **Context Awareness**: Remembers conversation history

---

## 🚀 Quick Start

### Prerequisites
- Python 3.10 or higher
- pip (Python package manager)
- Modern web browser (Chrome recommended for voice features)

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/Anushasmilee09/EveryLinguaAI-VoiceBot.git
```

2. **Create virtual environment** (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment**
```bash
# Copy example config
cp .env.example .env

# Edit .env and add your API key
# Required: GEMINI_API_KEY
```

5. **Run the application**
```bash
python app.py
```

6. **Access the app**
- Main App: http://localhost:5000
- Dealer Dashboard: http://localhost:5000/dealer_dashboard.html
- Dealer Locator: http://localhost:5000/dealer_locator.html

---

## 🔧 Configuration

### Required Environment Variables

| Variable | Description | How to Get |
|----------|-------------|------------|
| `GEMINI_API_KEY` | Google Gemini API key | [Google AI Studio](https://aistudio.google.com/app/apikey) |

### Optional Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_MODEL` | Gemini model to use | `gemini-2.5-flash` |
| `PORT` | Server port | `5000` |
| `FLASK_ENV` | Flask environment | `development` |
| `VOICE_ASSISTANT_ENABLED` | Enable background voice | `0` |

See `.env.example` for all available options.

---

## 📁 Project Structure

```
EveryLinguaAI/
├── app.py                  # Main Flask application
├── index.html              # Main web interface
├── dealer_dashboard.html   # Dealer management dashboard
├── dealer_locator.html     # Interactive dealer map
├── register.html           # User registration page
│
├── dealership_logic.py     # Bike catalog & dealership data
├── user_db.py              # User authentication & sessions
├── voice_assistant.py      # Voice recognition handler
├── tts_service.py          # Text-to-speech service
├── otp_service.py          # OTP generation & verification
├── crm_integration.py      # Booking management
├── human_agent_fallback.py # Support escalation
├── location_service.py     # Geolocation services
│
├── sw.js                   # Service worker (PWA)
├── manifest.json           # PWA manifest
│
├── requirements.txt        # Python dependencies
├── .env.example            # Environment template
├── Procfile                # Deployment config
├── render.yaml             # Render.com deployment
│
└── README.md               # This file
```

---

## 🔌 API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |
| POST | `/api/auth/logout` | Logout user |
| POST | `/api/auth/validate` | Validate session |

### Dealership
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/bikes` | Get all bikes |
| GET | `/api/services` | Get service packages |
| GET | `/api/dealerships` | Get all dealerships |
| POST | `/api/chat` | Send chat message |

### Bookings
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/test-ride-booking` | Book test ride |
| POST | `/api/service-booking` | Book service |
| GET | `/api/customer-dashboard/<id>` | Get customer data |

### Voice & TTS
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/voice-command` | Process voice command |
| POST | `/api/tts/generate` | Generate TTS audio |
| GET | `/api/tts/audio/<filename>` | Get TTS audio file |

---

## 🌐 Supported Languages

| Code | Language | Native Name |
|------|----------|-------------|
| en-US | English | English |
| hi-IN | Hindi | हिंदी |
| mr-IN | Marathi | मराठी |
| gu-IN | Gujarati | ગુજરાતી |
| ta-IN | Tamil | தமிழ் |
| te-IN | Telugu | తెలుగు |
| kn-IN | Kannada | ಕನ್ನಡ |
| bn-IN | Bengali | বাংলা |

---

## 🏢 Dealership Locations

| City | Locations |
|------|-----------|
| Mumbai | Mumbai Central, Andheri |
| Pune | Hinjewadi |
| Delhi NCR | Connaught Place, Dwarka, Gurgaon, Noida |
| Bangalore | Indiranagar, Whitefield |
| Chennai | Anna Nagar |
| Hyderabad | Jubilee Hills, Hi-Tech City |
| Other | Ahmedabad, Surat, Kolkata, Jaipur, Kochi, Coimbatore, Indore, Lucknow |

---

## 📱 PWA Support

EveryLingua AI is a Progressive Web App (PWA) with:
- ✅ Offline functionality
- ✅ Installable on desktop/mobile
- ✅ Push notifications (optional)
- ✅ Background sync for bookings

---

## 🚀 Deployment

### Render.com (Recommended)
1. Connect your GitHub repository
2. Create a new Web Service
3. Set environment variables
4. Deploy automatically

### Manual Deployment
```bash
# Production server
gunicorn app:app --bind 0.0.0.0:$PORT
```

---

## 🔒 Security Features

- Password hashing with SHA256
- Session token authentication
- CORS protection
- HTTP-only cookies
- OTP verification
- Input validation

---

## 🧪 Testing

```bash
# Run system tests
python test_system.py

# Test TTS functionality
python test_tts_multilingual.py
```

---

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---
