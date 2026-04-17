# EveryLingua AI - Project Workflow Documentation

## 📋 Table of Contents
1. [System Overview](#system-overview)
2. [Architecture Diagram](#architecture-diagram)
3. [Component Workflows](#component-workflows)
4. [Data Flow Diagrams](#data-flow-diagrams)
5. [API Endpoints Reference](#api-endpoints-reference)
6. [User Journey Flows](#user-journey-flows)

---

## 🏗️ System Overview

**EveryLingua AI** is a comprehensive multilingual voice assistant system for motorcycle dealerships. It combines AI-powered conversations, voice recognition, text-to-speech synthesis, and customer relationship management.

### Core Technologies
- **Backend**: Python Flask
- **AI Engine**: Google Gemini API
- **Voice Recognition**: Google Speech Recognition
- **Text-to-Speech**: gTTS (Google Text-to-Speech) + Google Cloud TTS
- **Translation**: Google Translator
- **Database**: SQLite
- **Deployment**: Render

### Supported Languages
- English (en-US, en-IN)
- Hindi (hi-IN)
- Tamil (ta-IN)
- Telugu (te-IN)
- Kannada (kn-IN)
- Marathi (mr-IN)
- Gujarati (gu-IN)
- Bengali (bn-IN)
- Malayalam (ml-IN)

---

## 🏛️ Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              CLIENT LAYER                                    │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────────┐  ┌─────────────────┐  ┌───────────┐ │
│  │  index.html  │  │dealer_dashboard  │  │ dealer_locator  │  │ register  │ │
│  │  (Main App)  │  │     .html        │  │     .html       │  │   .html   │ │
│  └──────┬───────┘  └────────┬─────────┘  └────────┬────────┘  └─────┬─────┘ │
│         │                   │                     │                  │       │
│         └───────────────────┴─────────────────────┴──────────────────┘       │
│                                     │                                        │
│                            [HTTP/REST API]                                   │
└─────────────────────────────────────┼───────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼───────────────────────────────────────┐
│                              API LAYER (Flask)                               │
├─────────────────────────────────────┼───────────────────────────────────────┤
│                              ┌──────┴──────┐                                 │
│                              │   app.py    │                                 │
│                              │ (Flask App) │                                 │
│                              └──────┬──────┘                                 │
│                                     │                                        │
│  ┌──────────────────────────────────┼──────────────────────────────────┐    │
│  │                          API ENDPOINTS                               │    │
│  ├──────────────────────────────────┼──────────────────────────────────┤    │
│  │  /api/chat          /api/bikes         /api/services                │    │
│  │  /api/voice-command /api/dealerships   /api/test-ride-booking       │    │
│  │  /api/tts/generate  /api/tts/chat      /api/service-booking         │    │
│  │  /api/auth/*        /api/register/*    /api/human-agent/*           │    │
│  │  /api/location/*    /api/ivr/respond   /api/config                  │    │
│  └──────────────────────────────────┼──────────────────────────────────┘    │
└─────────────────────────────────────┼───────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼───────────────────────────────────────┐
│                           SERVICE LAYER                                      │
├─────────────────────────────────────┼───────────────────────────────────────┤
│  ┌────────────────┐  ┌──────────────┴─────────────┐  ┌────────────────────┐ │
│  │ openai_client  │  │    dealership_logic.py     │  │  voice_assistant   │ │
│  │    .py         │  │                            │  │       .py          │ │
│  │ (Gemini AI)    │  │  - Bike Inventory          │  │  - Wake Word       │ │
│  │                │  │  - Service Packages        │  │  - Speech Recog    │ │
│  │ - Chat         │  │  - Dealerships             │  │  - Conversation    │ │
│  │ - TTS          │  │  - EMI Calculator          │  │  - Translation     │ │
│  │ - Translation  │  │  - NL Query Processing     │  │                    │ │
│  └───────┬────────┘  └────────────┬───────────────┘  └─────────┬──────────┘ │
│          │                        │                            │            │
│  ┌───────┴────────┐  ┌────────────┴───────────────┐  ┌────────┴──────────┐ │
│  │ tts_service.py │  │   crm_integration.py       │  │ human_agent_      │ │
│  │                │  │                            │  │  fallback.py      │ │
│  │ - gTTS         │  │  - Customer Management     │  │                   │ │
│  │ - Audio Gen    │  │  - Booking System          │  │ - Query Escalate  │ │
│  │ - Multi-lang   │  │  - Communication           │  │ - Agent Assign    │ │
│  │ - File Mgmt    │  │  - Email/SMS               │  │ - Dashboard       │ │
│  └────────────────┘  └────────────────────────────┘  └───────────────────┘ │
│                                                                             │
│  ┌────────────────┐  ┌────────────────────────────┐  ┌───────────────────┐ │
│  │ otp_service.py │  │   location_service.py      │  │    user_db.py     │ │
│  │                │  │                            │  │                   │ │
│  │ - Email OTP    │  │  - User Location           │  │ - User CRUD       │ │
│  │ - SMS OTP      │  │  - Nearest Dealer          │  │ - Sessions        │ │
│  │ - Verification │  │  - Location Queries        │  │ - Authentication  │ │
│  └────────────────┘  └────────────────────────────┘  └───────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼───────────────────────────────────────┐
│                          EXTERNAL SERVICES                                   │
├─────────────────────────────────────┼───────────────────────────────────────┤
│  ┌────────────────┐  ┌──────────────┴─────────────┐  ┌────────────────────┐ │
│  │ Google Gemini  │  │   Google Cloud TTS         │  │   SMTP Server      │ │
│  │     API        │  │                            │  │  (Gmail)           │ │
│  └────────────────┘  └────────────────────────────┘  └────────────────────┘ │
│                                                                             │
│  ┌────────────────┐  ┌────────────────────────────┐  ┌────────────────────┐ │
│  │ Google Speech  │  │   Google Maps API          │  │   SMS Gateway      │ │
│  │ Recognition    │  │                            │  │  (SMSLocal)        │ │
│  └────────────────┘  └────────────────────────────┘  └────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
┌─────────────────────────────────────┼───────────────────────────────────────┐
│                           DATA LAYER (SQLite)                                │
├─────────────────────────────────────┼───────────────────────────────────────┤
│  ┌────────────────┐  ┌──────────────┴─────────────┐  ┌────────────────────┐ │
│  │   users.db     │  │   dealership_crm.db        │  │   tts_output/      │ │
│  │                │  │                            │  │   (Audio Files)    │ │
│  │ - Users        │  │  - Customers               │  │                    │ │
│  │ - Sessions     │  │  - Bookings                │  │  - *.mp3 files     │ │
│  │ - OTPs         │  │  - Communications          │  │                    │ │
│  └────────────────┘  └────────────────────────────┘  └────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Component Workflows

### 1. Chat/Conversation Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CHAT WORKFLOW                                        │
└─────────────────────────────────────────────────────────────────────────────┘

User Input (Text/Voice)
        │
        ▼
┌───────────────────┐
│  /api/chat POST   │
│                   │
│  - message        │
│  - is_voice       │
│  - language       │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐     ┌─────────────────────┐
│ dealership_logic  │────▶│   GeminiClient      │
│ .py               │     │                     │
│                   │     │  - Generate AI      │
│ get_dealership_   │     │    response with    │
│ response()        │     │    locale support   │
└────────┬──────────┘     └─────────────────────┘
         │
         ▼
┌───────────────────┐
│ Context Building  │
│                   │
│ - Bike Inventory  │
│ - Services Data   │
│ - Dealer Info     │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Gemini AI Model   │
│ (gemini-2.5-flash)│
│                   │
│ - Process query   │
│ - Generate        │
│   multilingual    │
│   response        │
└────────┬──────────┘
         │
         ▼
┌───────────────────┐
│ Response Object   │
│                   │
│ { success: true,  │
│   response: "...",│
│   type: "...",    │
│   should_speak,   │
│   language }      │
└───────────────────┘
```

### 2. Voice Assistant Workflow (Desktop)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    VOICE ASSISTANT WORKFLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

        ┌─────────────────┐
        │  Start Voice    │
        │   Assistant     │
        └────────┬────────┘
                 │
                 ▼
        ┌─────────────────┐
        │ Microphone      │◀──────────────────┐
        │ Warm-up (4x)    │                   │
        └────────┬────────┘                   │
                 │                            │
                 ▼                            │
        ┌─────────────────┐                   │
        │ Listen for      │                   │
        │ Wake Word       │                   │
        │ "Hey Red"       │                   │
        └────────┬────────┘                   │
                 │                            │
         No      │      Yes                   │
    ┌────────────┴────────────┐               │
    │                         │               │
    ▼                         ▼               │
┌───────┐            ┌─────────────────┐      │
│ Retry │            │ Select Language │      │
└───────┘            └────────┬────────┘      │
                              │               │
                              ▼               │
                     ┌─────────────────┐      │
                     │ Conduct         │      │
                     │ Conversation    │      │
                     └────────┬────────┘      │
                              │               │
                              ▼               │
                     ┌─────────────────┐      │
                     │ Speech Recog    │      │
                     │ (Google API)    │      │
                     └────────┬────────┘      │
                              │               │
                              ▼               │
                     ┌─────────────────┐      │
                     │ Translate to    │      │
                     │ English (logic) │      │
                     └────────┬────────┘      │
                              │               │
                              ▼               │
                     ┌─────────────────┐      │
                     │ Dealership      │      │
                     │ Response        │      │
                     └────────┬────────┘      │
                              │               │
                              ▼               │
                     ┌─────────────────┐      │
                     │ Gemini AI       │      │
                     │ (Response in    │      │
                     │  user language) │      │
                     └────────┬────────┘      │
                              │               │
                              ▼               │
                     ┌─────────────────┐      │
                     │ Text-to-Speech  │      │
                     │ (Cloud TTS)     │      │
                     └────────┬────────┘      │
                              │               │
                              ▼               │
                     ┌─────────────────┐      │
                     │ Play Audio      │──────┘
                     │                 │
                     └─────────────────┘
```

### 3. Text-to-Speech (TTS) Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         TTS WORKFLOW                                         │
└─────────────────────────────────────────────────────────────────────────────┘

┌────────────────────┐
│ /api/tts/generate  │
│ OR                 │
│ /api/tts/chat      │
│                    │
│ Input:             │
│  - text            │
│  - language        │
│  - chat_id (opt)   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Language Mapping   │
│                    │
│ BCP-47 → gTTS      │
│ e.g., hi-IN → hi   │
│      ta-IN → ta    │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ TLD Selection      │
│                    │
│ Indian langs →     │
│   co.in            │
│ US English →       │
│   com              │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Generate Filename  │
│                    │
│ Hash-based for     │
│ caching            │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ gTTS Generation    │
│                    │
│ tts = gTTS(        │
│   text=text,       │
│   lang=lang,       │
│   tld=tld          │
│ )                  │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Save to            │
│ tts_output/*.mp3   │
└─────────┬──────────┘
          │
          ▼
┌────────────────────┐
│ Response:          │
│ { success: true,   │
│   audio_url,       │
│   filename,        │
│   file_size }      │
└────────────────────┘
```

### 4. User Authentication Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    USER AUTHENTICATION WORKFLOW                              │
└─────────────────────────────────────────────────────────────────────────────┘

                    ┌─────────────────┐
                    │    User         │
                    └────────┬────────┘
                             │
           ┌─────────────────┴─────────────────┐
           │                                   │
           ▼                                   ▼
┌─────────────────────┐            ┌─────────────────────┐
│   REGISTRATION      │            │      LOGIN          │
└─────────┬───────────┘            └──────────┬──────────┘
          │                                   │
          ▼                                   ▼
┌─────────────────────┐            ┌─────────────────────┐
│ /api/auth/send-otp  │            │ /api/auth/login     │
│                     │            │                     │
│ - identifier        │            │ - email             │
│ - method (email/sms)│            │ - password          │
└─────────┬───────────┘            │ - remember_me       │
          │                        └──────────┬──────────┘
          ▼                                   │
┌─────────────────────┐                       ▼
│ otp_service.py      │            ┌─────────────────────┐
│                     │            │ user_db.py          │
│ - Generate 6-digit  │            │                     │
│ - Send Email/SMS    │            │ authenticate_user() │
└─────────┬───────────┘            └──────────┬──────────┘
          │                                   │
          ▼                                   │
┌─────────────────────┐                       │
│ User enters OTP     │                       │
└─────────┬───────────┘                       │
          │                                   │
          ▼                                   │
┌─────────────────────┐                       │
│/api/register/verify │                       │
│        -otp         │                       │
└─────────┬───────────┘                       │
          │                                   │
          ▼                                   │
┌─────────────────────┐                       │
│ /api/auth/register  │                       │
│                     │                       │
│ - full_name         │                       │
│ - email             │                       │
│ - phone             │                       │
│ - password          │                       │
└─────────┬───────────┘                       │
          │                                   │
          └─────────────┬─────────────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Create Session      │
              │                     │
              │ - session_token     │
              │ - Set cookie        │
              │ - 12h or 2 days     │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Return User Data    │
              │ + Session Token     │
              └─────────────────────┘
```

### 5. Booking Workflow (Test Ride / Service)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BOOKING WORKFLOW                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐          ┌─────────────────────┐
│  Test Ride Booking  │          │  Service Booking    │
│                     │          │                     │
│ /api/test-ride-     │          │ /api/service-       │
│    booking          │          │    booking          │
└─────────┬───────────┘          └──────────┬──────────┘
          │                                 │
          └─────────────┬───────────────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ crm_integration.py  │
              │                     │
              │ Validate Input:     │
              │ - name              │
              │ - phone             │
              │ - bike_model        │
              │ - date              │
              │ - service_type (opt)│
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Create/Get Customer │
              │                     │
              │ customer_id =       │
              │ cust_{phone}_{date} │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Add to Customers    │
              │ Table               │
              │                     │
              │ Status: BOOKED_*    │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Create Booking      │
              │                     │
              │ booking_id =        │
              │ TR/SV{timestamp}    │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Add to Bookings     │
              │ Table               │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Send Notifications  │
              │                     │
              │ - Email             │
              │ - SMS               │
              └─────────┬───────────┘
                        │
                        ▼
              ┌─────────────────────┐
              │ Return Response     │
              │                     │
              │ { success: true,    │
              │   booking_id,       │
              │   message }         │
              └─────────────────────┘
```

### 6. Human Agent Escalation Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    HUMAN AGENT ESCALATION WORKFLOW                           │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────┐
│ User Query          │
└─────────┬───────────┘
          │
          ▼
┌─────────────────────┐
│ should_escalate_    │
│ to_human()          │
│                     │
│ Check keywords:     │
│ - complaint         │
│ - negotiate         │
│ - emergency         │
│ - custom            │
│ - technical         │
└─────────┬───────────┘
          │
    ┌─────┴─────┐
    │           │
   No          Yes
    │           │
    ▼           ▼
┌───────┐  ┌─────────────────────┐
│ AI    │  │ /api/human-agent/   │
│Handle │  │      escalate       │
└───────┘  └─────────┬───────────┘
                     │
                     ▼
           ┌─────────────────────┐
           │ Create Escalated    │
           │ Query               │
           │                     │
           │ - query_id          │
           │ - customer_id       │
           │ - reason            │
           │ - priority          │
           │ - status: pending   │
           └─────────┬───────────┘
                     │
                     ▼
           ┌─────────────────────┐
           │ Background Thread   │
           │ Assignment Loop     │
           │ (every 10 sec)      │
           └─────────┬───────────┘
                     │
                     ▼
           ┌─────────────────────┐
           │ find_best_agent()   │
           │                     │
           │ Score by:           │
           │ - expertise match   │
           │ - language match    │
           │ - availability      │
           │ - current load      │
           └─────────┬───────────┘
                     │
                     ▼
           ┌─────────────────────┐
           │ Assign to Agent     │
           │                     │
           │ - Update query      │
           │ - Notify agent      │
           │ - Status: assigned  │
           └─────────┬───────────┘
                     │
                     ▼
           ┌─────────────────────┐
           │ Agent Resolves      │
           │                     │
           │ /api/human-agent/   │
           │    resolve/{id}     │
           └─────────┬───────────┘
                     │
                     ▼
           ┌─────────────────────┐
           │ Return to Customer  │
           │                     │
           │ /api/human-agent/   │
           │    response/{id}    │
           └─────────────────────┘
```

---

## 📊 Data Flow Diagrams

### Main Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           MAIN DATA FLOW                                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐        ┌──────────────┐        ┌──────────────┐
│    User      │◀──────▶│   Browser    │◀──────▶│   Flask      │
│              │  I/O   │  (Frontend)  │  HTTP  │   Server     │
└──────────────┘        └──────────────┘        └──────┬───────┘
                                                       │
                        ┌──────────────────────────────┼──────────────────────┐
                        │                              │                      │
                        ▼                              ▼                      ▼
               ┌──────────────┐              ┌──────────────┐        ┌──────────────┐
               │  Gemini AI   │              │   SQLite     │        │   gTTS       │
               │              │              │   Database   │        │   Service    │
               │ - Chat       │              │              │        │              │
               │ - Context    │              │ - users.db   │        │ - MP3 Gen    │
               │ - Language   │              │ - crm.db     │        │ - Multi-lang │
               └──────────────┘              └──────────────┘        └──────────────┘
```

### Database Schema

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           DATABASE SCHEMA                                    │
└─────────────────────────────────────────────────────────────────────────────┘

                            users.db
┌─────────────────────────────────────────────────────────────────┐
│ users                          │ sessions                       │
├────────────────────────────────┼────────────────────────────────┤
│ id (PK)                        │ session_token (PK)             │
│ full_name                      │ user_id (FK)                   │
│ email (UNIQUE)                 │ created_at                     │
│ phone                          │ expires_at                     │
│ password_hash                  │ is_valid                       │
│ created_at                     └────────────────────────────────┤
│ verified                       │ otp_codes                      │
│ last_login                     ├────────────────────────────────┤
└────────────────────────────────┤ id (PK)                        │
                                 │ identifier                     │
                                 │ otp_code                       │
                                 │ created_at                     │
                                 │ expires_at                     │
                                 │ used                           │
                                 └────────────────────────────────┘

                         dealership_crm.db
┌─────────────────────────────────────────────────────────────────┐
│ customers                      │ bookings                       │
├────────────────────────────────┼────────────────────────────────┤
│ id (PK)                        │ id (PK)                        │
│ name                           │ customer_id (FK)               │
│ phone                          │ type                           │
│ email                          │ bike_model                     │
│ city                           │ service_type                   │
│ preferred_bikes (JSON)         │ date                           │
│ status                         │ status                         │
│ created_date                   │ notes                          │
│ last_contact                   │ created_date                   │
│ notes                          └────────────────────────────────┤
└────────────────────────────────┤ communications                 │
                                 ├────────────────────────────────┤
                                 │ id (PK)                        │
                                 │ customer_id (FK)               │
                                 │ type                           │
                                 │ subject                        │
                                 │ message                        │
                                 │ sent_date                      │
                                 │ status                         │
                                 └────────────────────────────────┘
```

---

## 🌐 API Endpoints Reference

### Authentication APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register new user |
| `/api/auth/login` | POST | User login |
| `/api/auth/logout` | POST | User logout |
| `/api/auth/validate` | GET/POST | Validate session |
| `/api/auth/send-otp` | POST | Send OTP for registration |
| `/api/register/send-otp` | POST | Send registration OTP |
| `/api/register/verify-otp` | POST | Verify OTP |
| `/api/register/resend-otp` | POST | Resend OTP |

### Chat & Voice APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/chat` | POST | Send chat message |
| `/api/voice-command` | POST | Process voice command |
| `/api/ivr/respond` | POST | IVR response (Gemini) |

### TTS APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/tts/generate` | POST | Generate TTS audio |
| `/api/tts/chat` | POST | Generate chat TTS |
| `/api/tts/audio/<filename>` | GET | Serve audio file |
| `/api/tts/files` | GET | List TTS files |
| `/api/tts/cleanup` | POST | Cleanup old files |

### Dealership APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/bikes` | GET | Get available bikes |
| `/api/bikes/search` | POST | Search bikes |
| `/api/bikes/emi` | POST | Calculate EMI |
| `/api/services` | GET | Get service packages |
| `/api/dealerships` | GET | Get dealership locations |
| `/api/dealerships/nearby` | POST | Get nearby dealerships |

### Booking APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/test-ride-booking` | POST | Book test ride |
| `/api/service-booking` | POST | Book service |
| `/api/customer-dashboard/<id>` | GET | Customer dashboard |

### Location APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/location/set` | POST | Set user location |
| `/api/location/nearest-dealer` | GET | Get nearest dealer |

### Human Agent APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/human-agent/escalate` | POST | Escalate to human |
| `/api/human-agent/response/<id>` | GET | Get agent response |
| `/api/human-agent/dashboard` | GET | Agent dashboard |
| `/api/human-agent/status/<id>` | POST | Update agent status |
| `/api/human-agent/resolve/<id>` | POST | Resolve query |

### Utility APIs
| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/gemini-key` | GET | Get Gemini API key |
| `/api/config` | GET | Get public config |
| `/health` | GET | Health check |

---

## 👤 User Journey Flows

### 1. New User Registration & First Interaction

```
┌─────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐  ┌─────────┐  ┌──────────┐
│Visit│─▶│ Register │─▶│  OTP    │─▶│ Verify   │─▶│ Login   │─▶│  Chat/   │
│Site │  │  Page    │  │Received │  │  OTP     │  │ Success │  │  Voice   │
└─────┘  └──────────┘  └─────────┘  └──────────┘  └─────────┘  └──────────┘
```

### 2. Bike Inquiry Flow

```
┌─────────┐  ┌───────────┐  ┌────────────┐  ┌───────────┐  ┌───────────┐
│ "Show   │─▶│ AI Process│─▶│ Inventory  │─▶│ Response  │─▶│ TTS Audio │
│  bikes" │  │ Query     │  │ Data       │  │ Generated │  │ (if voice)│
└─────────┘  └───────────┘  └────────────┘  └───────────┘  └───────────┘
                                                │
                                                ▼
                                      ┌───────────────────┐
                                      │ "Want EMI info?"  │
                                      │        │          │
                                      │        ▼          │
                                      │ EMI Calculation   │
                                      └───────────────────┘
```

### 3. Test Ride Booking Flow

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│"Book     │─▶│ Collect  │─▶│ CRM      │─▶│ Email/   │─▶│Booking   │
│test ride"│  │ Details  │  │ Create   │  │ SMS Sent │  │Confirmed │
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
                  │
                  ▼
            ┌──────────┐
            │ - Name   │
            │ - Phone  │
            │ - Bike   │
            │ - Date   │
            └──────────┘
```

### 4. Service Booking with Escalation

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│"Custom   │─▶│ AI Can't │─▶│ Escalate │─▶│ Agent    │─▶│ Human    │
│ service" │  │ Handle   │  │ to Human │  │ Assigned │  │ Response │
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

### 5. Multilingual Voice Interaction

```
┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
│ Voice    │─▶│ Speech   │─▶│ Gemini   │─▶│ Response │─▶│ TTS in   │
│ Input    │  │ Recog    │  │ Process  │  │ in User  │  │ User     │
│ (Hindi)  │  │ (hi-IN)  │  │ (locale) │  │ Language │  │ Language │
└──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
```

---

## 🚀 Deployment Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         DEPLOYMENT WORKFLOW                                  │
└─────────────────────────────────────────────────────────────────────────────┘

┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│   GitHub     │────▶│    Render    │────▶│  Production  │
│   Push       │     │   Build      │     │   Server     │
└──────────────┘     └──────┬───────┘     └──────────────┘
                            │
                            ▼
                   ┌──────────────────┐
                   │ Build Steps:     │
                   │                  │
                   │ 1. pip install   │
                   │    -r require-   │
                   │    ments.txt     │
                   │                  │
                   │ 2. gunicorn      │
                   │    app:app       │
                   │    --bind        │
                   │    0.0.0.0:$PORT │
                   └──────────────────┘

Environment Variables Required:
┌────────────────────────────────────────┐
│ GEMINI_API_KEY                         │
│ EMAIL_SENDER                           │
│ EMAIL_PASSWORD                         │
│ EMAIL_SMTP_SERVER                      │
│ EMAIL_SMTP_PORT                        │
│ GOOGLE_APPLICATION_CREDENTIALS         │
│ FLASK_ENV                              │
│ SERVICE_CENTER_NUMBER                  │
└────────────────────────────────────────┘
```

---

## 📁 File Structure Overview

```
EveryLinguaAI/
├── app.py                    # Main Flask application
├── main.py                   # Alternative entry point
├── openai_client.py          # Gemini AI client
├── dealership_logic.py       # Business logic
├── voice_assistant.py        # Voice assistant (desktop)
├── tts_service.py            # Text-to-Speech service
├── crm_integration.py        # CRM system
├── human_agent_fallback.py   # Human escalation
├── otp_service.py            # OTP verification
├── user_db.py                # User database
├── location_service.py       # Location services
├── audio.py                  # Audio playback
├── languages.py              # Language mappings
├── 
├── index.html                # Main web interface
├── register.html             # Registration page
├── dealer_dashboard.html     # Dealer dashboard
├── dealer_locator.html       # Dealer map locator
├── sw.js                     # Service worker
├── manifest.json             # PWA manifest
├── 
├── requirements.txt          # Python dependencies
├── Procfile                  # Render deployment
├── render.yaml               # Render config
├── .env                      # Environment variables
├── 
├── tts_output/               # Generated audio files
├── 
├── README.md                 # Project documentation
├── WORKFLOW.md               # This file
├── IMPLEMENTATION_STATUS.md  # Implementation status
├── USER_FEATURES_GUIDE.md    # User features guide
└── *.md                      # Other documentation
```

---

## 🔧 Configuration Summary

### Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `GEMINI_API_KEY` | Google Gemini AI | ✅ |
| `GEMINI_MODEL` | Model name (default: gemini-2.5-flash) | ❌ |
| `EMAIL_SENDER` | SMTP email sender | ✅ |
| `EMAIL_PASSWORD` | SMTP password | ✅ |
| `EMAIL_SMTP_SERVER` | SMTP server | ✅ |
| `EMAIL_SMTP_PORT` | SMTP port | ✅ |
| `GOOGLE_APPLICATION_CREDENTIALS` | Google Cloud credentials | ❌ |
| `VOICE_ASSISTANT_ENABLED` | Enable desktop voice | ❌ |
| `SERVICE_CENTER_NUMBER` | Service phone number | ❌ |
| `FLASK_ENV` | development/production | ❌ |

---

*Generated for EveryLingua AI Motorcycle Dealership Voice Assistant*
