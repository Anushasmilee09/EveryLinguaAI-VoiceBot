# EveryLingua AI - User Features Guide

## Overview
EveryLingua AI is a multilingual voice assistant for motorcycle dealership services with complete user registration, authentication, and voice playback controls.

---

## 🆕 New Features

### 1. **User Registration with OTP Verification**

#### How to Register:
1. Navigate to `/register.html` or click "Sign In / Register" on the homepage
2. Fill in your details:
   - Full Name
   - Email Address
   - Phone Number
   - Password (minimum 8 characters)
   - Confirm Password
3. Choose verification method:
   - **Email**: Receive OTP via email
   - **SMS**: Receive OTP via text message
4. Accept Terms & Conditions
5. Click "Send Verification Code"

#### OTP Verification:
1. Check your email/SMS for a 6-digit code
2. Enter the code in the verification screen
3. Code expires in 5 minutes
4. Can resend code if not received
5. Account is created upon successful verification

#### Features:
- ✅ Real-time form validation
- ✅ Password strength checking
- ✅ Auto-focus OTP inputs
- ✅ Paste OTP support
- ✅ Countdown timer
- ✅ Resend code option
- ✅ Session management

---

### 2. **Voice Playback Controls**

#### Stop/Resume Functionality:

When the voice assistant is speaking, you'll see a control panel with:

**Pause Button** 
- Click to pause the voice response
- Button changes to "Play" when paused
- Click again to resume from where it stopped

**Stop Button**
- Completely stops the voice playback
- Cannot be resumed once stopped
- Clears the current speech queue

**Volume Button**
- Controls system volume (browser-dependent)

#### Keyboard Shortcuts:
- `Space`: Start/Stop listening
- `Escape`: Stop everything (listening + speaking)
- `Ctrl/Cmd + K`: Clear conversation

#### Visual Indicators:
- **Purple indicator**: Speaking
- **Yellow indicator**: Paused
- **Green indicator**: Ready
- **Blue indicator**: Listening

---

### 3. **User Session Management**

#### Logged In Features:
- Personalized greeting with your name
- Session persists across page refreshes
- Access to all voice assistant features
- Logout option in header

#### Guest Mode:
- Can still use voice assistant
- Limited personalization
- Prompt to register for full features

#### Session Storage:
```javascript
localStorage.userRegistered = 'true'
localStorage.userName = 'Your Name'
localStorage.userEmail = 'your@email.com'
```

---

## 🎤 Multilingual Voice Features

### Supported Languages:
1. **English** (en-US)
2. **Hindi** (hi-IN) - हिंदी
3. **Tamil** (ta-IN) - தமிழ்
4. **Telugu** (te-IN) - తెలుగు
5. **Kannada** (kn-IN) - ಕನ್ನಡ
6. **Malayalam** (ml-IN) - മലയാളം
7. **Gujarati** (gu-IN) - ગુજરાતી
8. **Marathi** (mr-IN) - मराठी
9. **Bengali** (bn-IN) - বাংলা

### Voice Features:
- **Native Language Speech**: Speaks in pure native language without English mixing
- **Language-Specific Voices**: Optimized voices for each Indian language
- **Automatic Cleaning**: Removes markdown and special characters before speech
- **Fallback System**: Multiple fallback options if primary voice unavailable

### How to Use:
1. Select your preferred language from the language buttons
2. Start speaking in that language
3. Assistant responds in the same language
4. Voice output is in native script and pronunciation

---

## 📋 API Endpoints

### Registration & Authentication

#### Send OTP
```http
POST /api/register/send-otp
Content-Type: application/json

{
  "identifier": "email@example.com" or "+919876543210",
  "method": "email" or "sms"
}
```

**Response:**
```json
{
  "success": true,
  "message": "OTP sent successfully",
  "method": "email",
  "identifier": "email@example.com"
}
```

#### Verify OTP
```http
POST /api/register/verify-otp
Content-Type: application/json

{
  "identifier": "email@example.com",
  "otp": "123456"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Verification successful",
  "verified": true
}
```

#### Resend OTP
```http
POST /api/register/resend-otp
Content-Type: application/json

{
  "identifier": "email@example.com",
  "method": "email"
}
```

---

## 🎯 Quick Actions

The voice assistant provides quick actions for common tasks:

1. **Bike Models** - Browse available motorcycles
2. **Service Booking** - Schedule service appointments
3. **Test Ride** - Book a test ride
4. **Finance Options** - Calculate EMI and financing
5. **Find Dealer** - Interactive dealer locator
6. **Support** - Contact customer support

---

## 🔧 Troubleshooting

### Voice Not Working in Native Language?

**Check:**
1. Language is properly selected (check indicator in header)
2. Browser supports speech synthesis for that language
3. System has required language voices installed
4. Try refreshing the page
5. Check browser console for errors

### OTP Not Received?

**Solutions:**
1. Check spam/junk folder (for email)
2. Verify email/phone number is correct
3. Click "Resend Code" button
4. Wait 1-2 minutes for delivery
5. Try alternative verification method

### Voice Controls Not Appearing?

**Check:**
1. Response is being spoken (check status indicator)
2. Browser supports speech synthesis
3. Try clicking stop and starting again
4. Refresh the page if controls don't show

### Session Not Persisting?

**Check:**
1. Browser allows localStorage
2. Not in incognito/private mode
3. Clear browser cache and re-register
4. Check browser security settings

---

## 💡 Tips for Best Experience

### Voice Recognition:
- Speak clearly and at moderate pace
- Minimize background noise
- Use microphone close to your mouth
- Wait for "Listening..." indicator before speaking

### Language Selection:
- Choose language before starting conversation
- Stick to one language per conversation
- Voice assistant maintains language context

### Voice Playback:
- Use pause instead of stop if you want to resume
- Stop clears the speech queue completely
- Volume control depends on browser support

### Registration:
- Use valid email/phone for OTP verification
- Choose strong password (8+ characters)
- Save your credentials securely
- Complete verification within 5 minutes

---

## 🔐 Security & Privacy

### Data Storage:
- Passwords are never stored in localStorage
- Only session tokens and user identifiers stored
- OTP codes expire after 5 minutes
- Session data cleared on logout

### Voice Data:
- Voice is processed in real-time
- No voice recordings stored permanently
- Conversations are session-specific
- Can clear conversation anytime

### Best Practices:
- Logout when using shared devices
- Don't share OTP codes
- Use strong, unique passwords
- Clear browser data periodically

---

## 📱 Mobile Support

### Features:
- Fully responsive design
- Touch-friendly buttons
- Mobile-optimized voice controls
- PWA support (can be installed)

### Installation (PWA):
1. Open site in mobile browser
2. Click "Add to Home Screen"
3. App icon appears on home screen
4. Works like native app

---

## 🆘 Support

### Need Help?
- Use "Support" quick action
- Contact: 24/7 support available
- Email: support@everylinguaai.com
- Phone: Available in system

### Report Issues:
- Check console for errors
- Note your browser and OS
- Include steps to reproduce
- Share error messages if any

---

## 🚀 Coming Soon

- Social login (Google, Facebook)
- Voice biometric authentication
- Multi-device sync
- Offline mode support
- Voice commands customization
- Language auto-detection

---

## 📊 System Requirements

### Minimum:
- Modern browser (Chrome 80+, Firefox 75+, Safari 13+)
- Internet connection
- Microphone access
- Speakers/headphones

### Recommended:
- Latest browser version
- High-speed internet
- Quality microphone
- Quiet environment

---

## 🎓 Tutorial

### First Time Users:

1. **Start Here:**
   - Click "Sign In / Register"
   - Complete registration
   - Verify your account

2. **Setup Voice:**
   - Allow microphone access
   - Select your language
   - Test with "Hey Red"

3. **Explore Features:**
   - Try quick actions
   - Ask questions
   - Test voice controls

4. **Get Familiar:**
   - Practice with different languages
   - Try stop/resume
   - Explore dealer locator

---

## 📝 Changelog

### v2.0 (Latest)
- ✅ Added user registration with OTP
- ✅ Implemented voice playback controls
- ✅ Fixed multilingual TTS issues
- ✅ Added session management
- ✅ Enhanced voice quality
- ✅ Improved error handling

### v1.0 (Previous)
- Basic voice recognition
- Multiple language support
- Dealership integration
- Quick actions

---

For more information, visit the main documentation or contact support.