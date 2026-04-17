# SMS OTP Setup Guide

Your email OTP is already working! Now let's set up SMS delivery.

## Quick Setup (Choose ONE):

### Option 1: Fast2SMS (Recommended for India) ⭐

**Why Fast2SMS:**
- Free trial credits
- Works great in India
- Simple API
- No credit card required for testing

**Setup Steps:**
1. Go to https://www.fast2sms.com/
2. Sign up (free)
3. Get your API key from dashboard
4. Add to your `.env` file:

```env
# Add this to .env
FAST2SMS_API_KEY=your_api_key_here
```

**That's it!** SMS will work immediately.

---

### Option 2: Twilio (International)

**Why Twilio:**
- Works worldwide
- Very reliable
- More expensive
- Requires credit card

**Setup Steps:**
1. Go to https://www.twilio.com/
2. Sign up (get trial credits)
3. Get a phone number
4. Get your credentials
5. Add to `.env`:

```env
# Add these to .env
TWILIO_ACCOUNT_SID=your_account_sid
TWILIO_AUTH_TOKEN=your_auth_token
TWILIO_PHONE_NUMBER=+1234567890
```

---

### Option 3: MSG91 (India)

**Why MSG91:**
- Indian provider
- Good rates
- Reliable

**Setup Steps:**
1. Go to https://msg91.com/
2. Sign up
3. Get your auth key
4. Add to `.env`:

```env
# Add this to .env
MSG91_AUTH_KEY=your_auth_key
MSG91_TEMPLATE_ID=your_template_id  # Optional
```

---

## Current Configuration

Your `.env` file should look like this:

```env
GEMINI_API_KEY=AIzaSyBq7xdBUiToPh2Z38r06A2SIaS2SOFNZ1I

# Email Configuration (WORKING ✅)
EMAIL_SENDER=jayakrish5532@gmail.com
EMAIL_PASSWORD=dtzp tqlw blqr mhiu
EMAIL_SMTP_SERVER=smtp.gmail.com
EMAIL_SMTP_PORT=587

# SMS Configuration (ADD ONE OF THESE):
# Option 1: Fast2SMS (Recommended for India)
FAST2SMS_API_KEY=your_key_here

# Option 2: Twilio (Uncomment if using)
# TWILIO_ACCOUNT_SID=your_sid
# TWILIO_AUTH_TOKEN=your_token
# TWILIO_PHONE_NUMBER=+1234567890

# Option 3: MSG91 (Uncomment if using)
# MSG91_AUTH_KEY=your_key
# MSG91_TEMPLATE_ID=your_template_id

# Google Application Credentials
GOOGLE_APPLICATION_CREDENTIALS=C:\Users\jayak\Downloads\EveryLinguaAI-main\EveryLinguaAI-main\agentiicprojects-afb46a382025.json

VOICE_ASSISTANT_ENABLED=1
```

---

## Testing

### To Test Email OTP (Already Works):
1. Register with email address
2. Check your email inbox
3. Enter the OTP

### To Test SMS OTP (After Setup):
1. Add SMS provider key to `.env`
2. Restart `python app.py`
3. Register with phone number
4. Check your phone for SMS
5. Enter the OTP

---

## What Happens Now:

**With SMS Provider Configured:**
```
User registers → OTP sent to phone via Fast2SMS/Twilio → User receives SMS → Enters OTP → Verified ✅
```

**Without SMS Provider:**
```
User registers → OTP printed to console → User checks terminal → Enters OTP → Verified ✅
(Still works for testing!)
```

---

## Pricing

### Fast2SMS:
- ₹10 (~$0.12 USD) = 100 SMS
- Free trial credits available
- Pay as you go

### Twilio:
- $0.0079 per SMS (India)
- Free $15 trial credit
- Requires credit card

### MSG91:
- ₹0.15 per SMS
- Flexible plans

---

## Recommended: Fast2SMS

For your use case (India, testing), I recommend **Fast2SMS**:

1. **Sign up**: https://www.fast2sms.com/
2. **Copy API key** from dashboard
3. **Add to .env**:
   ```env
   FAST2SMS_API_KEY=your_actual_key_here
   ```
4. **Restart server**: `python app.py`
5. **Test**: Register with phone number!

---

## Troubleshooting

### SMS not received?

**Check:**
1. API key is correct in `.env`
2. Server was restarted after adding key
3. Phone number format is correct (10 digits for India)
4. Check SMS provider dashboard for credits
5. Check console for error messages

### Still showing OTP in console?

This means no provider is configured yet. The system works but SMS won't be sent. Follow the setup above!

### Email working but SMS not?

Email is configured correctly. Just add SMS provider key following the guide above.

---

## Quick Start (2 Minutes):

```bash
# 1. Get Fast2SMS key from https://www.fast2sms.com/
# 2. Add to .env:
echo "FAST2SMS_API_KEY=your_key_here" >> .env

# 3. Restart server
python app.py

# 4. Test it!
# Go to http://localhost:5000/register.html
# Choose SMS verification
# Enter your phone number
# You'll receive SMS with OTP!
```

---

## Support

If you need help:
1. Check console for detailed error messages
2. Verify API key is correct
3. Check SMS provider dashboard
4. Ensure you have credits/balance

The system is ready - just add your SMS provider key!