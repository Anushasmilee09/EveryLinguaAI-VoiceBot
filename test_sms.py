"""
Quick test to verify SMS OTP delivery via Twilio
"""
from otp_service import OTPService
import os
from dotenv import load_dotenv

load_dotenv()

def test_sms():
    print("=" * 50)
    print("SMS OTP Test (Twilio)")
    print("=" * 50)
    
    # Check if Twilio credentials are loaded
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    phone_number = os.getenv('TWILIO_PHONE_NUMBER')
    
    if account_sid and auth_token:
        print(f"✅ Twilio Account SID: {account_sid[:10]}...{account_sid[-5:]}")
        print(f"✅ Twilio Auth Token: {auth_token[:10]}...{auth_token[-5:]}")
        print(f"✅ Twilio Phone Number: {phone_number}")
    else:
        print("❌ Twilio credentials not found in environment")
        print("   Please add TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, TWILIO_PHONE_NUMBER to .env file")
        return
    
    # Initialize service
    service = OTPService()
    
    # Test phone number
    phone = "8925329304"
    otp = "123456"
    
    print(f"\n📱 Sending SMS to: {phone}")
    print(f"🔑 OTP: {otp}")
    print("\nAttempting to send...")
    
    # Send SMS
    success, message = service.send_sms_otp(phone, otp)
    
    print("\n" + "=" * 50)
    if success:
        print("✅ SMS SENT SUCCESSFULLY!")
        print(f"   Message: {message}")
        print(f"\n📲 Check your phone ({phone}) for the OTP!")
    else:
        print("❌ SMS FAILED!")
        print(f"   Error: {message}")
    print("=" * 50)

if __name__ == "__main__":
    test_sms()