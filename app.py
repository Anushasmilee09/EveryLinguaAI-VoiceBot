"""
Flask web server for the EveryLingua AI Motorcycle Dealership Voice Assistant
Serves the HTML interface and provides API endpoints for dealership operations
"""

from flask import Flask, render_template, jsonify, request, make_response, send_file, send_from_directory, Response
from flask_cors import CORS
from voice_assistant import VoiceAssistant
from dealership_logic import get_available_bikes, get_service_packages, get_dealerships
from crm_integration import create_test_ride_booking, create_service_booking, get_customer_dashboard
from human_agent_fallback import should_escalate_to_human, escalate_query, get_agent_response, get_agent_dashboard, update_agent_status, resolve_query
from location_service import set_user_location, get_nearest_dealership, process_location_query
from otp_service import send_registration_otp, verify_registration_otp, resend_registration_otp
from tts_service import generate_tts_audio, generate_chat_tts, list_tts_files, cleanup_old_files, TTS_OUTPUT_DIR
from ivr_service import handle_welcome, handle_menu, handle_route, handle_booking_status, handle_services, handle_hours, handle_agent
import user_db
import threading
import time
import os
from dotenv import load_dotenv
import requests

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Global voice assistant instance
voice_assistant = None

@app.route('/')
def index():
    """Serve the main HTML interface"""
    try:
        return app.send_static_file('index.html')
    except:
        with open('index.html', 'r', encoding='utf-8') as f:
            return f.read()

@app.route('/dealer_dashboard.html')
def dealer_dashboard():
    """Serve the dealer dashboard HTML interface"""
    try:
        return app.send_static_file('dealer_dashboard.html')
    except:
        with open('dealer_dashboard.html', 'r', encoding='utf-8') as f:
            return f.read()

@app.route('/dealer_locator.html')
def dealer_locator():
    """Serve the interactive dealer locator HTML interface"""
    try:
        return app.send_static_file('dealer_locator.html')
    except:
        with open('dealer_locator.html', 'r', encoding='utf-8') as f:
            return f.read()

@app.route('/register.html')
def register():
    """Serve the user registration HTML interface"""
    try:
        return app.send_static_file('register.html')
    except:
        with open('register.html', 'r', encoding='utf-8') as f:
            return f.read()

@app.route('/manifest.json')
def serve_manifest():
    """Serve the PWA manifest file"""
    try:
        with open('manifest.json', 'r', encoding='utf-8') as f:
            content = f.read()
        response = make_response(content)
        response.headers['Content-Type'] = 'application/json'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 404

@app.route('/sw.js')
def serve_service_worker():
    """Serve the service worker file"""
    try:
        with open('sw.js', 'r', encoding='utf-8') as f:
            content = f.read()
        response = make_response(content)
        response.headers['Content-Type'] = 'application/javascript'
        return response
    except Exception as e:
        return jsonify({"error": str(e)}), 404


@app.route('/api/bikes')
def get_bikes():
    """Get available bikes"""
    try:
        bikes = get_available_bikes()
        return jsonify({"success": True, "data": bikes})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/services')
def get_services():
    """Get service packages"""
    try:
        services = get_service_packages()
        return jsonify({"success": True, "data": services})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealerships')
def get_dealers():
    """Get dealership locations"""
    try:
        dealers = get_dealerships()
        return jsonify({"success": True, "data": dealers})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/chat', methods=['POST'])
def chat():
    """Handle chat messages from the frontend"""
    try:
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"success": False, "error": "No message provided"})

        message = data['message']
        is_voice_input = data.get('is_voice', False)  # Check if input came from voice
        language = data.get('language', 'en-US')  # Get language from frontend

        # Get response from dealership logic with language support
        from dealership_logic import get_dealership_response
        response = get_dealership_response(message, language)

        return jsonify({
            "success": True,
            "response": response,
            "type": "dealership" if "motorcycle" in response.lower() or "bike" in response.lower() else "general",
            "should_speak": is_voice_input,  # Only speak if input was voice
            "language": language
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/bikes/search', methods=['POST'])
def search_bikes():
    """Search bikes by query"""
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({"success": False, "error": "No query provided"})

        query = data['query']
        from dealership_logic import DealershipManager
        manager = DealershipManager()
        bikes = manager.search_bikes(query)

        return jsonify({
            "success": True,
            "data": [
                {
                    "id": bike.id,
                    "name": bike.name,
                    "brand": bike.brand,
                    "price": bike.price,
                    "category": bike.category.value,
                    "in_stock": bike.in_stock
                }
                for bike in bikes
            ]
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/bikes/emi', methods=['POST'])
def calculate_bike_emi():
    """Calculate EMI for a specific bike"""
    try:
        data = request.get_json()
        if not data or 'bike_id' not in data:
            return jsonify({"success": False, "error": "No bike_id provided"})

        bike_id = data['bike_id']
        down_payment = data.get('down_payment', 0.2)  # Default 20%
        tenure_months = data.get('tenure_months', 36)  # Default 3 years

        from dealership_logic import DealershipManager
        manager = DealershipManager()
        bike = manager.get_bike_details(bike_id)

        if not bike:
            return jsonify({"success": False, "error": "Bike not found"})

        emi_data = manager.calculate_emi(bike.price, bike.price * down_payment, tenure_months)

        return jsonify({
            "success": True,
            "bike": {
                "id": bike.id,
                "name": bike.name,
                "brand": bike.brand,
                "price": bike.price
            },
            "emi_calculation": emi_data
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealerships/nearby', methods=['POST'])
def get_nearby_dealerships():
    """Get nearby dealerships based on user location"""
    try:
        data = request.get_json()
        if not data or 'latitude' not in data or 'longitude' not in data:
            return jsonify({"success": False, "error": "Location coordinates required"})

        latitude = data['latitude']
        longitude = data['longitude']

        from dealership_logic import get_dealerships
        from location_service import get_nearest_dealership

        dealers = get_dealerships()
        nearest = get_nearest_dealership(dealers)

        return jsonify({
            "success": True,
            "nearest_dealership": nearest,
            "all_dealerships": dealers
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/voice-command', methods=['POST'])
def voice_command():
    """Handle voice commands from the frontend"""
    try:
        data = request.get_json()
        if not data or 'command' not in data:
            return jsonify({"success": False, "error": "No command provided"})

        command = data['command']

        # Process the voice command
        response = process_voice_command(command)

        return jsonify({"success": True, "response": response})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/test-ride-booking', methods=['POST'])
def book_test_ride():
    """Book a test ride with CRM integration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        result = create_test_ride_booking(
            customer_name=data.get('name'),
            phone=data.get('phone'),
            bike_model=data.get('bike_model'),
            preferred_date=data.get('date'),
            email=data.get('email', ''),
            city=data.get('city', '')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/service-booking', methods=['POST'])
def book_service():
    """Book a service with CRM integration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        result = create_service_booking(
            customer_name=data.get('name'),
            phone=data.get('phone'),
            bike_model=data.get('bike_model'),
            service_type=data.get('service_type'),
            preferred_date=data.get('date'),
            email=data.get('email', '')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/customer-dashboard/<customer_id>')
def customer_dashboard(customer_id):
    """Get customer dashboard data"""
    try:
        result = get_customer_dashboard(customer_id)
        return jsonify(result)
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/location/set', methods=['POST'])
def set_location():
    """Set user location"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        set_user_location(
            latitude=data.get('latitude'),
            longitude=data.get('longitude'),
            city=data.get('city', ''),
            state=data.get('state', '')
        )

        return jsonify({"success": True, "message": "Location updated"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/location/nearest-dealer')
def nearest_dealer():
    """Get nearest dealership"""
    try:
        from dealership_logic import get_dealerships
        dealers = get_dealerships()
        nearest = get_nearest_dealership(dealers)

        if nearest:
            return jsonify({"success": True, "data": nearest})
        else:
            return jsonify({"success": False, "error": "No dealerships found"})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/human-agent/escalate', methods=['POST'])
def escalate_to_human():
    """Escalate query to human agent"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        result = escalate_query(
            customer_id=data.get('customer_id', 'unknown'),
            query=data.get('query'),
            reason=data.get('reason', 'complex_query'),
            priority=data.get('priority', 1),
            language=data.get('language', 'en')
        )

        return jsonify(result)

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/human-agent/response/<query_id>')
def get_human_response(query_id):
    """Get response from human agent"""
    try:
        response = get_agent_response(query_id)
        if response:
            return jsonify({"success": True, "data": response})
        else:
            return jsonify({"success": False, "error": "No response found"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/human-agent/dashboard')
def agent_dashboard():
    """Get human agent dashboard data"""
    try:
        data = get_agent_dashboard()
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/human-agent/status/<agent_id>', methods=['POST'])
def update_agent_status_endpoint(agent_id):
    """Update agent status"""
    try:
        data = request.get_json()
        if not data or 'status' not in data:
            return jsonify({"success": False, "error": "No status provided"})

        from human_agent_fallback import AgentStatus
        status = AgentStatus(data['status'])

        success = update_agent_status(agent_id, status)
        return jsonify({"success": success})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/human-agent/resolve/<query_id>', methods=['POST'])
def resolve_human_query(query_id):
    """Resolve query with human agent response"""
    try:
        data = request.get_json()
        if not data or 'response' not in data:
            return jsonify({"success": False, "error": "No response provided"})

        success = resolve_query(query_id, data['response'])
        return jsonify({"success": success})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/gemini-key')
def get_gemini_key():
    """Get Gemini API key for frontend"""
    try:
        # Get API key from environment variables
        gemini_api_key = os.getenv('GEMINI_API_KEY')
        if not gemini_api_key:
            return jsonify({"success": False, "error": "Gemini API key not configured"})

        return jsonify({"success": True, "api_key": gemini_api_key})

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/register/send-otp', methods=['POST'])
def send_otp():
    """Send OTP for user registration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        identifier = data.get('identifier')  # email or phone
        method = data.get('method', 'email')  # 'email' or 'sms'

        if not identifier:
            return jsonify({"success": False, "error": "Email or phone number required"})

        # Validate method
        if method not in ['email', 'sms']:
            return jsonify({"success": False, "error": "Invalid verification method"})

        # Send OTP
        success, message = send_registration_otp(identifier, method)

        return jsonify({
            "success": success,
            "message": message,
            "method": method,
            "identifier": identifier
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/register/verify-otp', methods=['POST'])
def verify_otp():
    """Verify OTP for user registration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        identifier = data.get('identifier')
        otp = data.get('otp')

        if not identifier or not otp:
            return jsonify({"success": False, "error": "Identifier and OTP required"})

        # Verify OTP
        success, message = verify_registration_otp(identifier, otp)

        return jsonify({
            "success": success,
            "message": message,
            "verified": success
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/register/resend-otp', methods=['POST'])
def resend_otp():
    """Resend OTP for user registration"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})

        identifier = data.get('identifier')
        method = data.get('method', 'email')

        if not identifier:
            return jsonify({"success": False, "error": "Email or phone number required"})

        # Resend OTP
        success, message = resend_registration_otp(identifier, method)

        return jsonify({
            "success": success,
            "message": message,
            "method": method
        })

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    """Register a new user - supports both direct registration and OTP verification"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        
        full_name = data.get('full_name')
        email = data.get('email')
        phone = data.get('phone')
        password = data.get('password')
        identifier = data.get('identifier')  # email or phone for OTP
        otp = data.get('otp')
        method = data.get('method', 'email')
        skip_otp = data.get('skip_otp', False)  # Allow skipping OTP for direct registration
        
        # Validate required fields
        if not all([full_name, email, password]):
            return jsonify({"success": False, "error": "Name, email and password are required"})
        
        # If OTP is provided and not a bypass code, verify it
        if otp and otp != '000000' and not skip_otp:
            otp_result = user_db.verify_otp(identifier or email, otp)
            if not otp_result['success']:
                return jsonify(otp_result)
        
        # Create user directly
        result = user_db.create_user(full_name, email, phone, password)
        if not result['success']:
            return jsonify(result)
        
        # Mark user as verified (for direct registration without OTP)
        user_db.verify_user(email)
        
        # Create session with "remember me" enabled by default (2 days)
        session_result = user_db.create_session(result['user_id'], remember_me=True)
        
        if session_result['success']:
            # Set cookie and return response
            response_data = {
                "success": True,
                "message": "Registration successful",
                "user": {
                    "id": result['user_id'],
                    "name": full_name,
                    "full_name": full_name,
                    "email": email
                },
                "session_token": session_result['session_token']
            }
            
            response = make_response(jsonify(response_data))
            response.set_cookie('session_token', session_result['session_token'],
                              max_age=2*24*60*60, httponly=True, samesite='Lax')
            return response
        
        return jsonify({
            "success": True,
            "message": "Registration successful",
            "user": {
                "id": result['user_id'],
                "name": full_name,
                "email": email
            }
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    """Login user and create session"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        
        email = data.get('email')
        password = data.get('password')
        remember_me = data.get('remember_me', False)
        
        if not email or not password:
            return jsonify({"success": False, "error": "Email and password required"})
        
        # Authenticate user
        auth_result = user_db.authenticate_user(email, password)
        if not auth_result['success']:
            return jsonify(auth_result)
        
        user = auth_result['user']
        
        # Create session
        session_result = user_db.create_session(user['id'], remember_me=remember_me)
        
        if session_result['success']:
            # Return user with 'name' field for frontend compatibility
            response_data = {
                "success": True,
                "message": "Login successful",
                "user": {
                    "id": user['id'],
                    "name": user['full_name'],
                    "email": user['email'],
                    "verified": user.get('verified', True)
                },
                "session_token": session_result['session_token']
            }
            
            response = make_response(jsonify(response_data))
            
            # Set cookie with appropriate expiry
            max_age = 2*24*60*60 if remember_me else 12*60*60  # 2 days or 12 hours
            response.set_cookie('session_token', session_result['session_token'],
                              max_age=max_age, httponly=True, samesite='Lax')
            return response
        
        return jsonify(session_result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/auth/logout', methods=['POST'])
def logout_user():
    """Logout user and delete session"""
    try:
        session_token = request.cookies.get('session_token')
        
        if session_token:
            user_db.delete_session(session_token)
        
        response = make_response(jsonify({
            "success": True,
            "message": "Logged out successfully"
        }))
        response.set_cookie('session_token', '', expires=0)
        return response
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/auth/validate', methods=['GET', 'POST'])
def validate_session():
    """Validate current session"""
    try:
        # Try to get session token from POST body first, then cookies
        session_token = None
        if request.method == 'POST':
            data = request.get_json()
            if data:
                session_token = data.get('session_token')
        
        if not session_token:
            session_token = request.cookies.get('session_token')
        
        if not session_token:
            return jsonify({"valid": False, "error": "No session found"})
        
        result = user_db.validate_session(session_token)
        
        if result['success']:
            return jsonify({
                "valid": True,
                "user": {
                    "id": result['user']['id'],
                    "name": result['user']['full_name'],
                    "email": result['user']['email']
                }
            })
        else:
            return jsonify({"valid": False, "error": result.get('message', 'Invalid session')})
        
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)})

@app.route('/api/auth/send-otp', methods=['POST'])
def send_auth_otp():
    """Send OTP for registration (integrates with existing OTP service)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        
        identifier = data.get('identifier')
        method = data.get('method', 'email')
        
        if not identifier:
            return jsonify({"success": False, "error": "Email or phone required"})
        
        # Generate and send OTP
        success, message = send_registration_otp(identifier, method)
        
        if success:
            # Also save to database
            import random
            otp_code = ''.join([str(random.randint(0, 9)) for _ in range(6)])
            user_db.save_otp(identifier, otp_code)
        
        return jsonify({
            "success": success,
            "message": message,
            "method": method
        })
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/config')
def get_config():
    """Public config for frontend (non-secret)"""
    try:
        number = os.getenv('SERVICE_CENTER_NUMBER', '9566743579')
        # Normalize to E.164 if 10-digit India number
        normalized = number
        if number and number.isdigit() and len(number) == 10:
            normalized = '+91' + number
        elif number and number.startswith('+'):
            normalized = number
        else:
            normalized = number  # leave as-is

        return jsonify({
            "success": True,
            "service_center_number": normalized,
            "supported_languages": ["en-US","hi-IN","mr-IN","gu-IN","ta-IN","te-IN","kn-IN","bn-IN"]
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/ivr/respond', methods=['POST'])
def ivr_respond():
    """Proxy Gemini to generate short IVR responses in the requested language"""
    try:
        data = request.get_json() or {}
        message = (data.get('message') or '').strip()
        language = data.get('language', 'en-US')
        if not message:
            return jsonify({"success": False, "error": "No message provided"})

        api_key = os.getenv('GEMINI_API_KEY')
        if not api_key:
            return jsonify({"success": False, "error": "Gemini API key not configured"})

        system_preamble = (
            f"You are an IVR assistant for EveryLingua Motors service center. "
            f"Respond in the user's language/locale: {language}. "
            f"Keep answers conversational, concise (1–2 short sentences), no markdown, no lists. "
            f"If you need to ask a question, ask only one at a time."
        )

        # Use the active configured model (default gemini-2.5-flash) for IVR to ensure multilingual support
        model_name = os.getenv('GEMINI_MODEL', 'gemini-2.5-flash')
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
        payload = {
            "contents": [{
                "parts": [{"text": f"{system_preamble}\n\nUser: {message}"}]
            }]
        }

        r = requests.post(url, json=payload, timeout=15)
        r.raise_for_status()
        j = r.json()
        text = ""
        try:
            text = j["candidates"][0]["content"]["parts"][0]["text"]
        except Exception:
            pass
        if not text:
            text = "Sorry, I am unable to answer right now."

        return jsonify({"success": True, "text": text, "language": language})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def process_voice_command(command: str) -> str:
    """Process a voice command and return appropriate response"""
    from dealership_logic import get_dealership_response

    # Get response from dealership system
    response = get_dealership_response(command)

    return response

# ============================================
# Dealer Dashboard API Endpoints
# ============================================

@app.route('/api/dealer/stats')
def dealer_stats():
    """Get dashboard statistics"""
    try:
        from crm_integration import crm_manager
        stats = crm_manager.get_dashboard_stats()
        return jsonify({"success": True, "data": stats})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/customers', methods=['GET'])
def dealer_customers_list():
    """List all customers with search/filter"""
    try:
        from crm_integration import crm_manager
        search = request.args.get('search', '')
        status = request.args.get('status', '')
        customers = crm_manager.get_all_customers(search, status)
        return jsonify({"success": True, "data": customers})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/customers', methods=['POST'])
def dealer_customers_add():
    """Add a new customer"""
    try:
        from crm_integration import crm_manager, Customer, CustomerStatus
        data = request.get_json()
        if not data or not data.get('name') or not data.get('phone'):
            return jsonify({"success": False, "error": "Name and phone are required"})
        from datetime import datetime
        customer_id = f"cust_{data['phone']}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        customer = Customer(
            id=customer_id, name=data['name'], phone=data['phone'],
            email=data.get('email', ''), city=data.get('city', ''),
            status=CustomerStatus(data.get('status', 'new')),
            notes=data.get('notes', '')
        )
        success = crm_manager.add_customer(customer)
        if success:
            return jsonify({"success": True, "customer_id": customer_id, "message": "Customer added"})
        return jsonify({"success": False, "error": "Failed to add customer"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/customers/<customer_id>', methods=['PUT'])
def dealer_customers_update(customer_id):
    """Update customer"""
    try:
        from crm_integration import crm_manager
        data = request.get_json()
        success = crm_manager.update_customer(customer_id, data)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/customers/<customer_id>', methods=['DELETE'])
def dealer_customers_delete(customer_id):
    """Delete customer"""
    try:
        from crm_integration import crm_manager
        success = crm_manager.delete_customer(customer_id)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/bookings')
def dealer_bookings_list():
    """List all bookings"""
    try:
        from crm_integration import crm_manager
        type_filter = request.args.get('type', '')
        status_filter = request.args.get('status', '')
        bookings = crm_manager.get_all_bookings(type_filter, status_filter)
        return jsonify({"success": True, "data": bookings})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/bookings/<booking_id>', methods=['PUT'])
def dealer_bookings_update(booking_id):
    """Update booking status"""
    try:
        from crm_integration import crm_manager
        data = request.get_json()
        status = data.get('status') if data else None
        if not status:
            return jsonify({"success": False, "error": "Status required"})
        success = crm_manager.update_booking_status(booking_id, status)
        return jsonify({"success": success})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/inventory')
def dealer_inventory_list():
    """Get bike inventory"""
    try:
        from dealership_logic import get_available_bikes
        bikes = get_available_bikes()
        return jsonify({"success": True, "data": bikes})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/communications')
def dealer_communications_list():
    """Get communication history"""
    try:
        from crm_integration import crm_manager
        customer_id = request.args.get('customer_id', '')
        comms = crm_manager.get_all_communications(customer_id)
        return jsonify({"success": True, "data": comms})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/communications/send', methods=['POST'])
def dealer_communications_send():
    """Send a message to a customer"""
    try:
        from crm_integration import crm_manager, Communication, CommunicationType
        from datetime import datetime
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        comm_type = data.get('type', 'email')
        customer_id = data.get('customer_id', '')
        subject = data.get('subject', '')
        message = data.get('message', '')
        comm = Communication(
            id=f"comm_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            customer_id=customer_id,
            type=CommunicationType(comm_type),
            subject=subject, message=message,
            sent_date=datetime.now().isoformat(),
            status="sent"
        )
        crm_manager.add_communication(comm)
        return jsonify({"success": True, "message": "Message sent and logged"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/communications/bulk', methods=['POST'])
def dealer_communications_bulk():
    """Send bulk message to customer segment"""
    try:
        from crm_integration import crm_manager, Communication, CommunicationType
        from datetime import datetime
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        segment = data.get('segment', 'all')
        message = data.get('message', '')
        subject = data.get('subject', '')
        msg_type = data.get('type', 'email')
        customers = crm_manager.get_all_customers(status_filter=segment if segment != 'all' else '')
        sent_count = 0
        for cust in customers:
            comm = Communication(
                id=f"comm_bulk_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{sent_count}",
                customer_id=cust['id'],
                type=CommunicationType(msg_type),
                subject=subject, message=message,
                sent_date=datetime.now().isoformat(),
                status="sent"
            )
            crm_manager.add_communication(comm)
            sent_count += 1
        return jsonify({"success": True, "sent_count": sent_count, "message": f"Bulk message sent to {sent_count} customers"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/reports')
def dealer_reports():
    """Get analytics report data"""
    try:
        from crm_integration import crm_manager
        report = crm_manager.get_report_data()
        return jsonify({"success": True, "data": report})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/settings', methods=['GET'])
def dealer_settings_get():
    """Get dealership settings"""
    try:
        from crm_integration import crm_manager
        settings = crm_manager.get_settings()
        return jsonify({"success": True, "data": settings})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/settings', methods=['PUT'])
def dealer_settings_update():
    """Update dealership settings"""
    try:
        from crm_integration import crm_manager
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        success = crm_manager.update_settings(data)
        return jsonify({"success": success, "message": "Settings updated" if success else "Failed"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/dealer/export')
def dealer_export():
    """Export data as CSV"""
    try:
        from crm_integration import crm_manager
        data_type = request.args.get('type', 'customers')
        csv_data = crm_manager.export_csv(data_type)
        response = make_response(csv_data)
        response.headers['Content-Type'] = 'text/csv'
        response.headers['Content-Disposition'] = f'attachment; filename={data_type}_export.csv'
        return response
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

def start_voice_assistant():
    """Start the voice assistant in a separate thread"""
    global voice_assistant
    try:
        voice_assistant = VoiceAssistant()
        print("Starting voice assistant...")
        voice_assistant.run()
    except Exception as e:
        print(f"Error starting voice assistant: {e}")

@app.route('/api/tts/generate', methods=['POST'])
def generate_tts():
    """Generate TTS audio file from text"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        
        text = data.get('text', '').strip()
        language = data.get('language', 'en-US')
        
        if not text:
            return jsonify({"success": False, "error": "No text provided"})
        
        # Generate TTS audio
        result = generate_tts_audio(text, language)
        
        if result['success']:
            # Return the file path and metadata
            return jsonify({
                "success": True,
                "file_url": f"/api/tts/audio/{result['filename']}",
                "filename": result['filename'],
                "language": result['language'],
                "file_size": result['file_size']
            })
        else:
            return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/tts/chat', methods=['POST'])
def generate_chat_tts_endpoint():
    """Generate TTS audio for chat response and return audio URL"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "No data provided"})
        
        text = data.get('text', '').strip()
        language = data.get('language', 'en-US')
        chat_id = data.get('chat_id')
        
        if not text:
            return jsonify({"success": False, "error": "No text provided"})
        
        # Generate TTS audio
        result = generate_chat_tts(text, language, chat_id)
        
        if result['success']:
            return jsonify({
                "success": True,
                "audio_url": f"/api/tts/audio/{result['filename']}",
                "filename": result['filename'],
                "language": result['language'],
                "file_size": result['file_size']
            })
        else:
            return jsonify(result)
        
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/tts/audio/<filename>')
def serve_tts_audio(filename):
    """Serve TTS audio file"""
    try:
        return send_from_directory(TTS_OUTPUT_DIR, filename, mimetype='audio/mpeg')
    except Exception as e:
        return jsonify({"success": False, "error": f"File not found: {str(e)}"}), 404


@app.route('/api/tts/files')
def get_tts_files():
    """List all generated TTS files"""
    try:
        files = list_tts_files()
        return jsonify({
            "success": True,
            "files": files,
            "count": len(files)
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/api/tts/cleanup', methods=['POST'])
def cleanup_tts_files():
    """Clean up old TTS files"""
    try:
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)
        max_files = data.get('max_files', 100)
        
        deleted = cleanup_old_files(max_age_hours, max_files)
        
        return jsonify({
            "success": True,
            "deleted_count": deleted,
            "message": f"Cleaned up {deleted} old TTS files"
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy", "timestamp": time.time()})

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"success": False, "error": "Endpoint not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"success": False, "error": "Internal server error"}), 500

# ==========================================
# IVR WEBHOOK ROUTES (Twilio)
# ==========================================

@app.route('/api/ivr/welcome', methods=['GET', 'POST'])
def ivr_welcome():
    return Response(handle_welcome(), mimetype='application/xml')

@app.route('/api/ivr/menu', methods=['GET', 'POST'])
def ivr_menu():
    digits = request.values.get('Digits', '1')
    return Response(handle_menu(digits), mimetype='application/xml')

@app.route('/api/ivr/route', methods=['GET', 'POST'])
def ivr_route():
    digits = request.values.get('Digits', '')
    lang = request.args.get('lang', 'en')
    return Response(handle_route(digits, lang), mimetype='application/xml')

@app.route('/api/ivr/booking-status', methods=['GET', 'POST'])
def ivr_booking_status():
    digits = request.values.get('Digits', '')
    lang = request.args.get('lang', 'en')
    return Response(handle_booking_status(digits, lang), mimetype='application/xml')

@app.route('/api/ivr/services', methods=['GET', 'POST'])
def ivr_services():
    lang = request.args.get('lang', 'en')
    return Response(handle_services(lang), mimetype='application/xml')

@app.route('/api/ivr/hours', methods=['GET', 'POST'])
def ivr_hours():
    lang = request.args.get('lang', 'en')
    return Response(handle_hours(lang), mimetype='application/xml')

@app.route('/api/ivr/agent', methods=['GET', 'POST'])
def ivr_agent():
    lang = request.args.get('lang', 'en')
    return Response(handle_agent(lang), mimetype='application/xml')

if __name__ == '__main__':
    # Optional voice assistant startup (enable with VOICE_ASSISTANT_ENABLED=1 / true / yes)
    va_enabled = os.getenv('VOICE_ASSISTANT_ENABLED', '0').lower() in ('1', 'true', 'yes')
    if va_enabled:
        voice_thread = threading.Thread(target=start_voice_assistant, daemon=True)
        voice_thread.start()
    else:
        print("Voice assistant disabled (set VOICE_ASSISTANT_ENABLED=1 to enable).")

    # Get port from environment variable (for Render deployment)
    port = int(os.environ.get('PORT', 5000))

    # Start Flask server
    print("Starting EveryLingua AI Motorcycle Dealership Server...")
    print(f"Web interface available at: http://localhost:{port}")
    print(f"Dealer dashboard available at: http://localhost:{port}/dealer_dashboard.html")
    print("API endpoints:")
    print("  - GET  /api/bikes - Get available bikes")
    print("  - GET  /api/services - Get service packages")
    print("  - GET  /api/dealerships - Get dealership locations")
    print("  - POST /api/chat - Send chat message")
    print("  - POST /api/voice-command - Process voice command")
    print("  - POST /api/test-ride-booking - Book test ride")
    print("  - POST /api/service-booking - Book service")
    print("  - GET  /api/customer-dashboard/<id> - Get customer dashboard")
    print("  - POST /api/location/set - Set user location")
    print("  - GET  /api/location/nearest-dealer - Get nearest dealer")
    print("  - POST /api/human-agent/escalate - Escalate to human agent")
    print("  - GET  /api/human-agent/response/<id> - Get agent response")
    print("  - GET  /api/human-agent/dashboard - Get agent dashboard")
    print("  - POST /api/human-agent/status/<id> - Update agent status")
    print("  - POST /api/human-agent/resolve/<id> - Resolve query")
    print("  - GET  /api/gemini-key - Get Gemini API key")
    print("  - GET  /health - Health check")

    # Use gunicorn for production, but allow debug mode for development
    if os.environ.get('FLASK_ENV') == 'production':
        # Production mode - let gunicorn handle it
        pass
    else:
        # Development mode
        app.run(host='0.0.0.0', port=port, debug=True)
