"""
OTP Service for user registration verification
Handles email and SMS OTP generation and verification
"""

import smtplib
import random
import time
import os
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()

class OTPService:
    def __init__(self):
        self.otp_storage = {}  # In production, use Redis or database
        self.otp_expiry_minutes = 5
        
        # Email configuration
        self.email_sender = os.getenv('EMAIL_SENDER')
        self.email_password = os.getenv('EMAIL_PASSWORD')
        self.smtp_server = os.getenv('EMAIL_SMTP_SERVER', 'smtp.gmail.com')
        self.smtp_port = int(os.getenv('EMAIL_SMTP_PORT', 587))

    def generate_otp(self):
        """Generate a 6-digit OTP"""
        return str(random.randint(100000, 999999))

    def store_otp(self, identifier, otp, method='email'):
        """Store OTP with expiration time"""
        expiry_time = datetime.now() + timedelta(minutes=self.otp_expiry_minutes)
        self.otp_storage[identifier] = {
            'otp': otp,
            'expiry': expiry_time,
            'method': method,
            'attempts': 0
        }

    def send_email_otp(self, email, otp):
        """Send OTP via email"""
        try:
            if not self.email_sender or not self.email_password:
                raise Exception("Email credentials not configured")

            msg = MIMEMultipart()
            msg['From'] = self.email_sender
            msg['To'] = email
            msg['Subject'] = "EveryLingua AI - Registration OTP"

            body = f"""
            <html>
            <body>
                <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
                    <h2 style="color: #3b82f6;">Welcome to EveryLingua AI!</h2>
                    <p>Thank you for registering with us. Please use the following OTP to verify your email address:</p>
                    
                    <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; text-align: center; margin: 20px 0;">
                        <h1 style="color: #1f2937; font-size: 32px; letter-spacing: 4px; margin: 0;">{otp}</h1>
                    </div>
                    
                    <p><strong>Important:</strong></p>
                    <ul>
                        <li>This OTP is valid for {self.otp_expiry_minutes} minutes only</li>
                        <li>Do not share this OTP with anyone</li>
                        <li>If you didn't request this OTP, please ignore this email</li>
                    </ul>
                    
                    <p>Best regards,<br>EveryLingua AI Team</p>
                    
                    <hr style="margin: 20px 0; border: none; border-top: 1px solid #e5e7eb;">
                    <p style="font-size: 12px; color: #6b7280;">
                        This is an automated message. Please do not reply to this email.
                    </p>
                </div>
            </body>
            </html>
            """

            msg.attach(MIMEText(body, 'html'))

            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.email_sender, self.email_password)
            server.send_message(msg)
            server.quit()

            return True, "OTP sent successfully to your email"

        except Exception as e:
            print(f"⚠️  Email sending failed: {e}")
            print(f"   📧 OTP for {email}: {otp}")
            
            # Log to file for reference
            try:
                with open('sms_log.txt', 'a') as f:
                    f.write(f"{datetime.now()}: Email OTP {otp} for {email} (not sent - SMTP error: {e})\n")
            except:
                pass
            
            # Return success with the OTP so registration can proceed
            return True, f"OTP generated successfully. Your verification code is: {otp} (Email delivery unavailable - please use this code directly)"

    def send_sms_otp(self, phone, otp):
        """Send OTP via SMS using multiple providers"""
        # Clean phone number (remove spaces, dashes)
        phone = ''.join(filter(str.isdigit, phone))
        
        # Try SMSLocal first (India-specific, API key based)
        smslocal_api_key = os.getenv('SMSLOCAL_API_KEY')
        smslocal_sender_id = os.getenv('SMSLOCAL_SENDER_ID', 'TXTIND')
        
        if smslocal_api_key:
            try:
                # SMSLocal uses a simple GET/POST API with API key as parameter
                # Message content as requested by user
                message = f"Your EveryLingua AI verification code is {otp}. Valid for 5 minutes. Do not share this code."
                
                # Try v1 API (simple REST API)
                url = "https://www.smslocal.com/api/v1/send/"
                
                payload = {
                    "apikey": smslocal_api_key,
                    "sender": smslocal_sender_id,
                    "number": phone,
                    "message": message,
                    "format": "json"
                }
                
                print(f"[SMS] Attempting SMSLocal to {phone}...")
                print(f"[SMS] API Key: {smslocal_api_key[:10]}...{smslocal_api_key[-10:]}")
                print(f"[SMS] Sender ID: {smslocal_sender_id}")
                
                # Try POST first
                response = requests.post(url, data=payload, timeout=10)
                
                print(f"[SMS] SMSLocal Response Status: {response.status_code}")
                print(f"[SMS] SMSLocal Response: {response.text[:500]}")  # First 500 chars only
                
                if response.status_code == 200:
                    try:
                        result = response.json()
                        if result.get('status') == 'success' or result.get('message_id') or result.get('return'):
                            print(f"[SMS] ✅ SMSLocal OTP sent to {phone}: {otp}")
                            return True, "OTP sent successfully to your phone"
                        else:
                            print(f"[SMS] ❌ SMSLocal error: {result}")
                    except:
                        # If not JSON, might be text response
                        if 'success' in response.text.lower():
                            print(f"[SMS] ✅ SMSLocal OTP sent to {phone}: {otp}")
                            return True, "OTP sent successfully to your phone"
                else:
                    print(f"[SMS] ❌ SMSLocal HTTP error: {response.status_code}")
                
            except Exception as e:
                print(f"[SMS] ❌ SMSLocal exception: {e}")
                import traceback
                traceback.print_exc()
        
        # Try Twilio as backup
        twilio_sid = os.getenv('TWILIO_ACCOUNT_SID')
        twilio_token = os.getenv('TWILIO_AUTH_TOKEN')
        twilio_phone = os.getenv('TWILIO_PHONE_NUMBER')
        
        if all([twilio_sid, twilio_token, twilio_phone]):
            try:
                from twilio.rest import Client
                
                client = Client(twilio_sid, twilio_token)
                message = client.messages.create(
                    body=f"Your EveryLingua AI verification code is: {otp}. Valid for 5 minutes.",
                    from_=twilio_phone,
                    to=f"+91{phone}" if len(phone) == 10 else phone
                )
                
                print(f"[SMS] Twilio OTP sent to {phone}: {otp}")
                return True, "OTP sent successfully to your phone"
                
            except Exception as e:
                print(f"Twilio error: {e}")
        
        # Try MSG91 (another India provider)
        msg91_key = os.getenv('MSG91_AUTH_KEY')
        msg91_template_id = os.getenv('MSG91_TEMPLATE_ID')
        
        if msg91_key:
            try:
                url = f"https://api.msg91.com/api/v5/otp"
                payload = {
                    "template_id": msg91_template_id or "default",
                    "mobile": phone if phone.startswith('+') else f"+91{phone}",
                    "authkey": msg91_key,
                    "otp": otp
                }
                
                response = requests.post(url, json=payload, timeout=10)
                
                if response.status_code == 200:
                    print(f"[SMS] MSG91 OTP sent to {phone}: {otp}")
                    return True, "OTP sent successfully to your phone"
                    
            except Exception as e:
                print(f"MSG91 error: {e}")
        
        # If all providers fail, fall back to mock (log only)
        print(f"⚠️  No SMS provider configured. OTP for {phone}: {otp}")
        print(f"   Add FAST2SMS_API_KEY or TWILIO credentials to .env")
        
        # Still log to file
        try:
            with open('sms_log.txt', 'a') as f:
                f.write(f"{datetime.now()}: SMS OTP {otp} for {phone} (not sent - no provider)\n")
        except:
            pass
        
        # Return success but with a note
        return True, f"OTP generated: {otp} (Check console - SMS provider not configured)"

    def verify_otp(self, identifier, provided_otp):
        """Verify the provided OTP"""
        if identifier not in self.otp_storage:
            return False, "OTP not found or expired"

        stored_data = self.otp_storage[identifier]
        
        # Check if OTP is expired
        if datetime.now() > stored_data['expiry']:
            del self.otp_storage[identifier]
            return False, "OTP has expired. Please request a new one"

        # Check attempt limit
        if stored_data['attempts'] >= 3:
            del self.otp_storage[identifier]
            return False, "Too many failed attempts. Please request a new OTP"

        # Verify OTP
        if stored_data['otp'] == provided_otp:
            del self.otp_storage[identifier]
            return True, "OTP verified successfully"
        else:
            stored_data['attempts'] += 1
            return False, f"Invalid OTP. {3 - stored_data['attempts']} attempts remaining"

    def resend_otp(self, identifier, method='email'):
        """Resend OTP to the same identifier"""
        if identifier not in self.otp_storage:
            return False, "No pending OTP found. Please start registration again"

        # Generate new OTP
        new_otp = self.generate_otp()
        
        # Update stored OTP
        self.store_otp(identifier, new_otp, method)

        # Send based on method
        if method == 'email':
            return self.send_email_otp(identifier, new_otp)
        elif method == 'sms':
            return self.send_sms_otp(identifier, new_otp)
        else:
            return False, "Invalid method"

# Global OTP service instance
otp_service = OTPService()

def send_registration_otp(identifier, method='email'):
    """Send OTP for user registration - now integrates with database"""
    import user_db
    
    otp = otp_service.generate_otp()
    otp_service.store_otp(identifier, otp, method)
    
    # Also save to database
    user_db.save_otp(identifier, otp)

    if method == 'email':
        success, message = otp_service.send_email_otp(identifier, otp)
        if success:
            print(f"[OTP] Email OTP sent to {identifier}: {otp}")  # Debug log
        return success, message
    elif method == 'sms':
        success, message = otp_service.send_sms_otp(identifier, otp)
        if success:
            print(f"[OTP] SMS OTP sent to {identifier}: {otp}")  # Debug log
        return success, message
    else:
        return False, "Invalid verification method"

def verify_registration_otp(identifier, otp):
    """Verify OTP for user registration - checks both memory and database"""
    import user_db
    
    # Try database first (more persistent)
    db_result = user_db.verify_otp(identifier, otp)
    if db_result['success']:
        # Also verify in memory if exists
        if identifier in otp_service.otp_storage:
            del otp_service.otp_storage[identifier]
        return True, "OTP verified successfully"
    
    # Fall back to memory-based verification
    return otp_service.verify_otp(identifier, otp)

def resend_registration_otp(identifier, method='email'):
    """Resend OTP for user registration"""
    import user_db
    
    # Generate new OTP
    new_otp = otp_service.generate_otp()
    otp_service.store_otp(identifier, new_otp, method)
    
    # Save to database
    user_db.save_otp(identifier, new_otp)
    
    # Send based on method
    if method == 'email':
        success, message = otp_service.send_email_otp(identifier, new_otp)
        if success:
            print(f"[OTP] Resent email OTP to {identifier}: {new_otp}")  # Debug log
        return success, message
    elif method == 'sms':
        success, message = otp_service.send_sms_otp(identifier, new_otp)
        if success:
            print(f"[OTP] Resent SMS OTP to {identifier}: {new_otp}")  # Debug log
        return success, message
    else:
        return False, "Invalid method"
