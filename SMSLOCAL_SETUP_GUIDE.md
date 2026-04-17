# 📱 SMSLocal Setup Guide

## 🎯 SMS Template Content for SMSLocal Dashboard

### Template Message (Exact Text):
```
Your EveryLingua AI verification code is {#var#}. Valid for 5 minutes. Do not share this code.
```

**Important Notes:**
- Use `{#var#}` exactly as shown - this is where the OTP number will be inserted
- Total length: Keep under 160 characters
- Type: Transactional (not Promotional)
- Language: English

---

## 📋 Step-by-Step Setup:

### Step 1: Create SMSLocal Account
1. Visit: https://www.smslocal.com/
2. Click "Sign Up" or "Register"
3. Complete registration form
4. Verify your email
5. Complete KYC (required for SMS sending in India)

### Step 2: Get Sender ID Approved
1. Login to SMSLocal dashboard
2. Go to "Sender IDs" section
3. Request sender ID: `TXTIND` (or your preferred 6-character ID)
4. Wait for approval (usually 1-2 business days)
5. Alternative: Use pre-approved generic sender ID if available

### Step 3: Create SMS Template
1. Go to "Templates" or "Content Templates" section
2. Click "Add New Template"
3. Fill in the form:

**Template Details:**
```
Template Name: EveryLingua OTP
Template Type: Transactional
Language: English
Template Content: Your EveryLingua AI verification code is {#var#}. Valid for 5 minutes. Do not share this code.
```

4. Submit for approval
5. Wait for DLT approval (usually 1-2 hours to 1 day)

### Step 4: Get API Credentials
1. Go to "API Settings" or "Developers" section
2. Find your credentials:
   - **Username**: Your login email or API username
   - **Password**: API password (not login password - generate if needed)

### Step 5: Update .env File
Open your `.env` file and add:
```env
SMSLOCAL_USERNAME=your_username_or_email
SMSLOCAL_PASSWORD=your_api_password
SMSLOCAL_SENDER_ID=TXTIND
```

Replace with your actual credentials:
- `your_username_or_email` - Your SMSLocal username/email
- `your_api_password` - Your API password from dashboard
- `TXTIND` - Your approved sender ID

### Step 6: Add Credits
1. Go to "Recharge" or "Add Money"
2. Minimum recommended: ₹100-₹500
3. Choose payment method (UPI/Card/Net Banking)
4. Complete payment

### Step 7: Test SMS
Run the test script:
```bash
python test_sms.py
```

Expected output:
```
✅ SMSLocal OTP sent to 8925329304: 123456
📲 Check your phone for the OTP!
```

---

## 💰 SMSLocal Pricing:

| SMS Type | Cost per SMS | 100 SMS Cost | 1000 SMS Cost |
|----------|--------------|--------------|---------------|
| Transactional OTP | ₹0.15 - ₹0.20 | ₹15-₹20 | ₹150-₹200 |
| Promotional | ₹0.10 - ₹0.15 | ₹10-₹15 | ₹100-₹150 |

**Recommended Credits:** Start with ₹200 for testing and early production

---

## 🔧 Configuration in .env File:

### Current Configuration:
```env
# SMS Configuration (SMSLocal)
SMSLOCAL_USERNAME=your_smslocal_username
SMSLOCAL_PASSWORD=your_smslocal_password
SMSLOCAL_SENDER_ID=TXTIND
```

### Example (After Setup):
```env
# SMS Configuration (SMSLocal)
SMSLOCAL_USERNAME=jayakrish5532@gmail.com
SMSLOCAL_PASSWORD=your_api_key_from_dashboard
SMSLOCAL_SENDER_ID=TXTIND
```

---

## 📝 SMS Template Variations:

If the default template doesn't work, try these alternatives:

### Template Option 1 (Current):
```
Your EveryLingua AI verification code is {#var#}. Valid for 5 minutes. Do not share this code.
```

### Template Option 2 (Shorter):
```
Your EveryLingua OTP is {#var#}. Valid for 5 minutes.
```

### Template Option 3 (With Brand):
```
EveryLingua: Your OTP is {#var#}. Valid 5 min. Do not share.
```

### Template Option 4 (Simple):
```
Your OTP: {#var#}. Valid for 5 minutes. - EveryLingua AI
```

---

## 🚀 After Setup Checklist:

- [ ] SMSLocal account created and verified
- [ ] Sender ID approved (TXTIND or similar)
- [ ] SMS template created and approved
- [ ] API credentials obtained
- [ ] .env file updated with credentials
- [ ] Account recharged (minimum ₹100)
- [ ] test_sms.py runs successfully
- [ ] SMS received on test phone number

---

## 🔍 Troubleshooting:

### Issue: SMS not sending
**Solution:**
1. Check if sender ID is approved
2. Verify template is approved by DLT
3. Ensure account has sufficient balance
4. Verify API credentials in .env
5. Check phone number format (10 digits, no +91)

### Issue: Template not approved
**Solution:**
1. Wait 24 hours for DLT approval
2. Ensure template follows TRAI guidelines
3. Use transactional category
4. Avoid promotional words

### Issue: Invalid credentials error
**Solution:**
1. Use API password, not login password
2. Generate new API key from dashboard
3. Check username (might be email or unique ID)

### Issue: Insufficient balance
**Solution:**
1. Add credits via dashboard
2. Minimum ₹100 recommended
3. Check current balance in dashboard

---

## 📞 SMSLocal Support:

- **Website**: https://www.smslocal.com/
- **Support Email**: support@smslocal.com
- **Documentation**: https://www.smslocal.com/docs/
- **API Docs**: https://www.smslocal.com/api-documentation/

---

## 🎊 API Integration Details:

### Endpoint:
```
POST https://www.smslocal.com/api/v2/send/
```

### Parameters:
```python
{
    "username": "your_username",
    "password": "your_api_password",
    "sender": "TXTIND",
    "mobile": "8925329304",
    "message": "Your EveryLingua AI verification code is 123456. Valid for 5 minutes. Do not share this code.",
    "type": "1"  # 1 = Transactional, 2 = Promotional
}
```

### Success Response:
```json
{
    "status": "success",
    "message_id": "12345678",
    "balance": 950.50
}
```

---

## ✅ Quick Setup Summary:

1. **Sign up** at https://www.smslocal.com/
2. **Get Sender ID** approved (e.g., TXTIND)
3. **Create template**: "Your EveryLingua AI verification code is {#var#}. Valid for 5 minutes. Do not share this code."
4. **Wait for approval** (1-2 days)
5. **Get API credentials** from dashboard
6. **Update .env** with username, password, sender_id
7. **Add credits** (minimum ₹100)
8. **Test**: Run `python test_sms.py`
9. **Done!** SMS will be sent automatically during registration

---

## 🎯 Template Content for Copy-Paste:

**Copy this exact text to SMSLocal template dashboard:**

```
Your EveryLingua AI verification code is {#var#}. Valid for 5 minutes. Do not share this code.
```

**Template Settings:**
- Name: EveryLingua OTP
- Type: Transactional
- Category: OTP/Verification
- Language: English
- Variable: {#var#} (for OTP number)

---

That's it! After completing these steps, your SMS OTP will work automatically. The system will replace `{#var#}` with the actual 6-digit OTP code when sending.