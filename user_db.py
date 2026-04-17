"""
User Database Management
Simple SQLite database for user authentication and session management
"""

import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
import os

DB_PATH = 'users.db'

def init_db():
    """Initialize the database with required tables"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            phone TEXT,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            verified BOOLEAN DEFAULT 0,
            last_login TIMESTAMP
        )
    ''')
    
    # Sessions table for "remember me"
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            session_token TEXT UNIQUE NOT NULL,
            expires_at TIMESTAMP NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    # OTP verification table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS otp_codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            identifier TEXT NOT NULL,
            otp_code TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            expires_at TIMESTAMP NOT NULL,
            verified BOOLEAN DEFAULT 0
        )
    ''')
    
    conn.commit()
    conn.close()
    print("Database initialized successfully")

def hash_password(password):
    """Hash a password using SHA256"""
    return hashlib.sha256(password.encode()).hexdigest()

def generate_session_token():
    """Generate a secure session token"""
    return secrets.token_urlsafe(32)

def create_user(full_name, email, phone, password):
    """Create a new user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
        cursor.execute('''
            INSERT INTO users (full_name, email, phone, password_hash)
            VALUES (?, ?, ?, ?)
        ''', (full_name, email, phone, password_hash))
        
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return {'success': True, 'user_id': user_id, 'message': 'User created successfully'}
    except sqlite3.IntegrityError:
        return {'success': False, 'message': 'Email already registered'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def verify_user(email):
    """Mark user as verified"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('UPDATE users SET verified = 1 WHERE email = ?', (email,))
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': 'User verified'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def authenticate_user(email, password):
    """Authenticate user with email and password"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        password_hash = hash_password(password)
        
        cursor.execute('''
            SELECT id, full_name, email, verified 
            FROM users 
            WHERE email = ? AND password_hash = ?
        ''', (email, password_hash))
        
        user = cursor.fetchone()
        
        if user:
            user_id, full_name, email, verified = user
            
            # Update last login
            cursor.execute('UPDATE users SET last_login = ? WHERE id = ?', 
                         (datetime.now(), user_id))
            conn.commit()
            conn.close()
            
            return {
                'success': True,
                'user': {
                    'id': user_id,
                    'full_name': full_name,
                    'email': email,
                    'verified': bool(verified)
                }
            }
        else:
            conn.close()
            return {'success': False, 'message': 'Invalid email or password'}
            
    except Exception as e:
        return {'success': False, 'message': str(e)}

def create_session(user_id, remember_me=False):
    """Create a session token for a user"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Clean up expired sessions
        cursor.execute('DELETE FROM sessions WHERE expires_at < ?', (datetime.now(),))
        
        # Create new session
        session_token = generate_session_token()
        
        # Remember me: 2 days, otherwise: 12 hours
        if remember_me:
            expires_at = datetime.now() + timedelta(days=2)
        else:
            expires_at = datetime.now() + timedelta(hours=12)
        
        cursor.execute('''
            INSERT INTO sessions (user_id, session_token, expires_at)
            VALUES (?, ?, ?)
        ''', (user_id, session_token, expires_at))
        
        conn.commit()
        conn.close()
        
        return {
            'success': True,
            'session_token': session_token,
            'expires_at': expires_at.isoformat()
        }
    except Exception as e:
        return {'success': False, 'message': str(e)}

def validate_session(session_token):
    """Validate a session token and return user info"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.user_id, u.full_name, u.email, s.expires_at
            FROM sessions s
            JOIN users u ON s.user_id = u.id
            WHERE s.session_token = ?
        ''', (session_token,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            user_id, full_name, email, expires_at = result
            expires_dt = datetime.fromisoformat(expires_at)
            
            if expires_dt > datetime.now():
                return {
                    'success': True,
                    'user': {
                        'id': user_id,
                        'full_name': full_name,
                        'email': email
                    }
                }
            else:
                # Session expired
                delete_session(session_token)
                return {'success': False, 'message': 'Session expired'}
        else:
            return {'success': False, 'message': 'Invalid session'}
            
    except Exception as e:
        return {'success': False, 'message': str(e)}

def delete_session(session_token):
    """Delete a session (logout)"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE session_token = ?', (session_token,))
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': 'Logged out successfully'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def save_otp(identifier, otp_code):
    """Save OTP code for verification"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Delete old OTPs for this identifier
        cursor.execute('DELETE FROM otp_codes WHERE identifier = ?', (identifier,))
        
        expires_at = datetime.now() + timedelta(minutes=5)
        
        cursor.execute('''
            INSERT INTO otp_codes (identifier, otp_code, expires_at)
            VALUES (?, ?, ?)
        ''', (identifier, otp_code, expires_at))
        
        conn.commit()
        conn.close()
        
        return {'success': True, 'message': 'OTP saved'}
    except Exception as e:
        return {'success': False, 'message': str(e)}

def verify_otp(identifier, otp_code):
    """Verify OTP code"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, expires_at, verified
            FROM otp_codes
            WHERE identifier = ? AND otp_code = ?
            ORDER BY created_at DESC
            LIMIT 1
        ''', (identifier, otp_code))
        
        result = cursor.fetchone()
        
        if result:
            otp_id, expires_at, verified = result
            expires_dt = datetime.fromisoformat(expires_at)
            
            if verified:
                conn.close()
                return {'success': False, 'message': 'OTP already used'}
            
            if expires_dt < datetime.now():
                conn.close()
                return {'success': False, 'message': 'OTP expired'}
            
            # Mark as verified
            cursor.execute('UPDATE otp_codes SET verified = 1 WHERE id = ?', (otp_id,))
            conn.commit()
            conn.close()
            
            return {'success': True, 'message': 'OTP verified successfully'}
        else:
            conn.close()
            return {'success': False, 'message': 'Invalid OTP'}
            
    except Exception as e:
        return {'success': False, 'message': str(e)}

def email_exists(email):
    """Check if email already exists in database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE email = ?', (email.lower().strip(),))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    except Exception as e:
        print(f"Error checking email: {e}")
        return False

def phone_exists(phone):
    """Check if phone already exists in database"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Normalize phone number (remove spaces, dashes, etc.)
        normalized_phone = ''.join(filter(str.isdigit, phone))
        
        cursor.execute('SELECT COUNT(*) FROM users WHERE REPLACE(REPLACE(phone, " ", ""), "-", "") LIKE ?', 
                      (f'%{normalized_phone[-10:]}%',))
        count = cursor.fetchone()[0]
        conn.close()
        
        return count > 0
    except Exception as e:
        print(f"Error checking phone: {e}")
        return False

def get_user_by_email(email):
    """Get user information by email"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, full_name, email, phone, verified, created_at, last_login
            FROM users
            WHERE email = ?
        ''', (email,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                'success': True,
                'user': {
                    'id': result[0],
                    'full_name': result[1],
                    'email': result[2],
                    'phone': result[3],
                    'verified': bool(result[4]),
                    'created_at': result[5],
                    'last_login': result[6]
                }
            }
        else:
            return {'success': False, 'message': 'User not found'}
            
    except Exception as e:
        return {'success': False, 'message': str(e)}

# Initialize database on import
if not os.path.exists(DB_PATH):
    init_db()
