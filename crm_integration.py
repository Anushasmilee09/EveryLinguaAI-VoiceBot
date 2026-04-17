"""
CRM Integration Module for Motorcycle Dealership
Handles customer relationship management, booking tracking, and customer communication
"""

import json
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

class CustomerStatus(Enum):
    NEW = "new"
    CONTACTED = "contacted"
    INTERESTED = "interested"
    BOOKED_TEST_RIDE = "booked_test_ride"
    BOOKED_SERVICE = "booked_service"
    PURCHASED = "purchased"
    INACTIVE = "inactive"

class CommunicationType(Enum):
    EMAIL = "email"
    SMS = "sms"
    PHONE = "phone"
    WHATSAPP = "whatsapp"

@dataclass
class Customer:
    id: str
    name: str
    phone: str
    email: str = ""
    city: str = ""
    preferred_bikes: List[str] = None
    status: CustomerStatus = CustomerStatus.NEW
    created_date: str = ""
    last_contact: str = ""
    notes: str = ""

    def __post_init__(self):
        if self.preferred_bikes is None:
            self.preferred_bikes = []
        if not self.created_date:
            self.created_date = datetime.now().isoformat()
        if not self.last_contact:
            self.last_contact = self.created_date

@dataclass
class Booking:
    id: str
    customer_id: str
    type: str  # "test_ride", "service", "purchase"
    bike_model: str = ""
    service_type: str = ""
    date: str = ""
    status: str = "confirmed"  # confirmed, completed, cancelled
    notes: str = ""
    created_date: str = ""

@dataclass
class Communication:
    id: str
    customer_id: str
    type: CommunicationType
    subject: str = ""
    message: str = ""
    sent_date: str = ""
    status: str = "sent"  # sent, delivered, failed

class CRMManager:
    """
    Manages customer relationships, bookings, and communications
    """

    def __init__(self, db_path: str = "dealership_crm.db"):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Customers table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT NOT NULL,
                email TEXT,
                city TEXT,
                preferred_bikes TEXT,
                status TEXT,
                created_date TEXT,
                last_contact TEXT,
                notes TEXT
            )
        ''')

        # Bookings table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bookings (
                id TEXT PRIMARY KEY,
                customer_id TEXT,
                type TEXT,
                bike_model TEXT,
                service_type TEXT,
                date TEXT,
                status TEXT,
                notes TEXT,
                created_date TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')

        # Communications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS communications (
                id TEXT PRIMARY KEY,
                customer_id TEXT,
                type TEXT,
                subject TEXT,
                message TEXT,
                sent_date TEXT,
                status TEXT,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        ''')

        conn.commit()
        conn.close()

    def add_customer(self, customer: Customer) -> bool:
        """Add a new customer to the database"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO customers (id, name, phone, email, city, preferred_bikes,
                                    status, created_date, last_contact, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (customer.id, customer.name, customer.phone, customer.email, customer.city,
                  json.dumps(customer.preferred_bikes), customer.status.value,
                  customer.created_date, customer.last_contact, customer.notes))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding customer: {e}")
            return False

    def get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer by ID"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            conn.close()

            if row:
                return Customer(
                    id=row[0],
                    name=row[1],
                    phone=row[2],
                    email=row[3],
                    city=row[4],
                    preferred_bikes=json.loads(row[5]) if row[5] else [],
                    status=CustomerStatus(row[6]),
                    created_date=row[7],
                    last_contact=row[8],
                    notes=row[9]
                )
            return None
        except Exception as e:
            print(f"Error getting customer: {e}")
            return None

    def update_customer_status(self, customer_id: str, status: CustomerStatus) -> bool:
        """Update customer status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                UPDATE customers SET status = ?, last_contact = ?
                WHERE id = ?
            ''', (status.value, datetime.now().isoformat(), customer_id))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating customer status: {e}")
            return False

    def add_booking(self, booking: Booking) -> bool:
        """Add a new booking"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO bookings (id, customer_id, type, bike_model, service_type,
                                   date, status, notes, created_date)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (booking.id, booking.customer_id, booking.type, booking.bike_model,
                  booking.service_type, booking.date, booking.status, booking.notes,
                  booking.created_date))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding booking: {e}")
            return False

    def get_customer_bookings(self, customer_id: str) -> List[Booking]:
        """Get all bookings for a customer"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute("SELECT * FROM bookings WHERE customer_id = ?", (customer_id,))
            rows = cursor.fetchall()
            conn.close()

            bookings = []
            for row in rows:
                bookings.append(Booking(
                    id=row[0],
                    customer_id=row[1],
                    type=row[2],
                    bike_model=row[3],
                    service_type=row[4],
                    date=row[5],
                    status=row[6],
                    notes=row[7],
                    created_date=row[8]
                ))
            return bookings
        except Exception as e:
            print(f"Error getting customer bookings: {e}")
            return []

    def add_communication(self, communication: Communication) -> bool:
        """Add a communication record"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO communications (id, customer_id, type, subject, message,
                                          sent_date, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (communication.id, communication.customer_id, communication.type.value,
                  communication.subject, communication.message, communication.sent_date,
                  communication.status))

            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error adding communication: {e}")
            return False

    def send_email(self, to_email: str, subject: str, message: str, customer_id: str = None) -> bool:
        """Send email to customer"""
        try:
            # Email configuration (you would configure this with your SMTP settings)
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', 587))
            sender_email = os.getenv('SENDER_EMAIL', 'noreply@everylingua.com')
            sender_password = os.getenv('SENDER_PASSWORD', '')

            if not sender_password:
                print("Email not configured - would send email to:", to_email)
                return True

            msg = MIMEMultipart()
            msg['From'] = sender_email
            msg['To'] = to_email
            msg['Subject'] = subject

            msg.attach(MIMEText(message, 'plain'))

            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(sender_email, sender_password)
            text = msg.as_string()
            server.sendmail(sender_email, to_email, text)
            server.quit()

            # Log communication
            if customer_id:
                comm = Communication(
                    id=f"comm_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    customer_id=customer_id,
                    type=CommunicationType.EMAIL,
                    subject=subject,
                    message=message,
                    sent_date=datetime.now().isoformat()
                )
                self.add_communication(comm)

            return True
        except Exception as e:
            print(f"Error sending email: {e}")
            return False

    def send_sms(self, phone: str, message: str, customer_id: str = None) -> bool:
        """Send SMS to customer"""
        try:
            # SMS configuration (you would integrate with an SMS service)
            sms_api_key = os.getenv('SMS_API_KEY', '')

            if not sms_api_key:
                print(f"SMS not configured - would send SMS to {phone}: {message}")
                return True

            # Here you would integrate with your SMS provider
            # For now, just log the communication
            if customer_id:
                comm = Communication(
                    id=f"comm_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    customer_id=customer_id,
                    type=CommunicationType.SMS,
                    message=message,
                    sent_date=datetime.now().isoformat()
                )
                self.add_communication(comm)

            return True
        except Exception as e:
            print(f"Error sending SMS: {e}")
            return False

    def create_test_ride_booking(self, customer_name: str, phone: str, bike_model: str,
                                preferred_date: str, email: str = "", city: str = "") -> Dict:
        """Create a test ride booking with CRM integration"""
        try:
            # Create or get customer
            customer_id = f"cust_{phone}_{datetime.now().strftime('%Y%m%d')}"

            customer = Customer(
                id=customer_id,
                name=customer_name,
                phone=phone,
                email=email,
                city=city,
                preferred_bikes=[bike_model],
                status=CustomerStatus.BOOKED_TEST_RIDE
            )

            if not self.add_customer(customer):
                return {"success": False, "message": "Failed to create customer record"}

            # Create booking
            booking_id = f"TR{datetime.now().strftime('%Y%m%d%H%M')}"
            booking = Booking(
                id=booking_id,
                customer_id=customer_id,
                type="test_ride",
                bike_model=bike_model,
                date=preferred_date,
                created_date=datetime.now().isoformat()
            )

            if not self.add_booking(booking):
                return {"success": False, "message": "Failed to create booking"}

            # Send confirmation
            confirmation_message = f"""
Dear {customer_name},

Your test ride for {bike_model} has been booked successfully!

Booking Details:
- Date: {preferred_date}
- Booking ID: {booking_id}
- Dealership: EveryLingua Motors

Please bring a valid driving license and arrive 15 minutes before the scheduled time.

For any changes, please contact us at +91-9876543210

Best regards,
EveryLingua Motors Team
"""

            self.send_email(email or f"{phone}@sms.everylingua.com", f"Test Ride Confirmation - {booking_id}", confirmation_message, customer_id)
            self.send_sms(phone, f"Test ride booked for {bike_model} on {preferred_date}. Booking ID: {booking_id}", customer_id)

            return {
                "success": True,
                "booking_id": booking_id,
                "message": f"Test ride booked successfully! Booking ID: {booking_id}"
            }

        except Exception as e:
            print(f"Error creating test ride booking: {e}")
            return {"success": False, "message": "Failed to create booking"}

    def create_service_booking(self, customer_name: str, phone: str, bike_model: str,
                             service_type: str, preferred_date: str, email: str = "") -> Dict:
        """Create a service booking with CRM integration"""
        try:
            # Create or get customer
            customer_id = f"cust_{phone}_{datetime.now().strftime('%Y%m%d')}"

            customer = Customer(
                id=customer_id,
                name=customer_name,
                phone=phone,
                email=email,
                preferred_bikes=[bike_model],
                status=CustomerStatus.BOOKED_SERVICE
            )

            if not self.add_customer(customer):
                return {"success": False, "message": "Failed to create customer record"}

            # Create booking
            booking_id = f"SV{datetime.now().strftime('%Y%m%d%H%M')}"
            booking = Booking(
                id=booking_id,
                customer_id=customer_id,
                type="service",
                bike_model=bike_model,
                service_type=service_type,
                date=preferred_date,
                created_date=datetime.now().isoformat()
            )

            if not self.add_booking(booking):
                return {"success": False, "message": "Failed to create booking"}

            # Send confirmation
            confirmation_message = f"""
Dear {customer_name},

Your service appointment has been booked successfully!

Booking Details:
- Bike: {bike_model}
- Service: {service_type}
- Date: {preferred_date}
- Booking ID: {booking_id}

Please arrive at the scheduled time with your bike and service book.

For any changes, please contact us at +91-9876543210

Best regards,
EveryLingua Motors Team
"""

            self.send_email(email or f"{phone}@sms.everylingua.com", f"Service Booking Confirmation - {booking_id}", confirmation_message, customer_id)
            self.send_sms(phone, f"Service booked for {bike_model} on {preferred_date}. Booking ID: {booking_id}", customer_id)

            return {
                "success": True,
                "booking_id": booking_id,
                "message": f"Service booked successfully! Booking ID: {booking_id}"
            }

        except Exception as e:
            print(f"Error creating service booking: {e}")
            return {"success": False, "message": "Failed to create booking"}

    def get_customer_dashboard_data(self, customer_id: str) -> Dict:
        """Get customer dashboard data"""
        try:
            customer = self.get_customer(customer_id)
            if not customer:
                return {"success": False, "message": "Customer not found"}

            bookings = self.get_customer_bookings(customer_id)

            return {
                "success": True,
                "customer": {
                    "name": customer.name,
                    "phone": customer.phone,
                    "email": customer.email,
                    "status": customer.status.value,
                    "preferred_bikes": customer.preferred_bikes
                },
                "bookings": [
                    {
                        "id": booking.id,
                        "type": booking.type,
                        "bike_model": booking.bike_model,
                        "service_type": booking.service_type,
                        "date": booking.date,
                        "status": booking.status
                    }
                    for booking in bookings
                ]
            }
        except Exception as e:
            print(f"Error getting customer dashboard data: {e}")
            return {"success": False, "message": "Failed to get dashboard data"}

    def get_all_customers(self, search: str = "", status_filter: str = "") -> List[Dict]:
        """Get all customers with optional search and filter"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            query = "SELECT * FROM customers"
            params = []
            conditions = []
            if search:
                conditions.append("(name LIKE ? OR phone LIKE ? OR email LIKE ? OR city LIKE ?)")
                params.extend([f"%{search}%"] * 4)
            if status_filter and status_filter != "all":
                conditions.append("status = ?")
                params.append(status_filter)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY created_date DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            return [{"id": r[0], "name": r[1], "phone": r[2], "email": r[3] or "",
                     "city": r[4] or "", "preferred_bikes": json.loads(r[5]) if r[5] else [],
                     "status": r[6] or "new", "created_date": r[7] or "", "last_contact": r[8] or "",
                     "notes": r[9] or ""} for r in rows]
        except Exception as e:
            print(f"Error getting customers: {e}")
            return []

    def update_customer(self, customer_id: str, data: Dict) -> bool:
        """Update customer fields"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            fields = []
            params = []
            for key in ["name", "phone", "email", "city", "status", "notes"]:
                if key in data:
                    fields.append(f"{key} = ?")
                    params.append(data[key])
            if not fields:
                return False
            fields.append("last_contact = ?")
            params.append(datetime.now().isoformat())
            params.append(customer_id)
            cursor.execute(f"UPDATE customers SET {', '.join(fields)} WHERE id = ?", params)
            conn.commit()
            conn.close()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Error updating customer: {e}")
            return False

    def delete_customer(self, customer_id: str) -> bool:
        """Delete a customer and associated records"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM communications WHERE customer_id = ?", (customer_id,))
            cursor.execute("DELETE FROM bookings WHERE customer_id = ?", (customer_id,))
            cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error deleting customer: {e}")
            return False

    def get_all_bookings(self, type_filter: str = "", status_filter: str = "") -> List[Dict]:
        """Get all bookings with optional filters"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            query = """SELECT b.*, c.name as customer_name, c.phone as customer_phone
                       FROM bookings b LEFT JOIN customers c ON b.customer_id = c.id"""
            params = []
            conditions = []
            if type_filter and type_filter not in ("all", ""):
                conditions.append("b.type = ?")
                params.append(type_filter)
            if status_filter and status_filter not in ("all", ""):
                conditions.append("b.status = ?")
                params.append(status_filter)
            if conditions:
                query += " WHERE " + " AND ".join(conditions)
            query += " ORDER BY b.created_date DESC"
            cursor.execute(query, params)
            rows = cursor.fetchall()
            conn.close()
            return [{"id": r[0], "customer_id": r[1], "type": r[2], "bike_model": r[3] or "",
                     "service_type": r[4] or "", "date": r[5] or "", "status": r[6] or "confirmed",
                     "notes": r[7] or "", "created_date": r[8] or "",
                     "customer_name": r[9] if len(r) > 9 else "", "customer_phone": r[10] if len(r) > 10 else ""
                     } for r in rows]
        except Exception as e:
            print(f"Error getting bookings: {e}")
            return []

    def update_booking_status(self, booking_id: str, status: str) -> bool:
        """Update booking status"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("UPDATE bookings SET status = ? WHERE id = ?", (status, booking_id))
            conn.commit()
            affected = cursor.rowcount
            conn.close()
            return affected > 0
        except Exception as e:
            print(f"Error updating booking: {e}")
            return False

    def get_all_communications(self, customer_id: str = "") -> List[Dict]:
        """Get all communications with optional customer filter"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            if customer_id:
                cursor.execute("""SELECT cm.*, c.name as customer_name FROM communications cm
                                  LEFT JOIN customers c ON cm.customer_id = c.id
                                  WHERE cm.customer_id = ? ORDER BY cm.sent_date DESC""", (customer_id,))
            else:
                cursor.execute("""SELECT cm.*, c.name as customer_name FROM communications cm
                                  LEFT JOIN customers c ON cm.customer_id = c.id
                                  ORDER BY cm.sent_date DESC""")
            rows = cursor.fetchall()
            conn.close()
            return [{"id": r[0], "customer_id": r[1], "type": r[2], "subject": r[3] or "",
                     "message": r[4] or "", "sent_date": r[5] or "", "status": r[6] or "sent",
                     "customer_name": r[7] if len(r) > 7 else ""} for r in rows]
        except Exception as e:
            print(f"Error getting communications: {e}")
            return []

    def get_dashboard_stats(self) -> Dict:
        """Get aggregate dashboard statistics"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            total_customers = cursor.fetchone()[0]
            today = datetime.now().strftime("%Y-%m-%d")
            cursor.execute("SELECT COUNT(*) FROM bookings WHERE date LIKE ?", (f"{today}%",))
            today_bookings = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'confirmed'")
            pending_bookings = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM bookings WHERE status = 'completed'")
            completed_bookings = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM bookings WHERE type = 'test_ride'")
            test_rides = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM bookings WHERE type = 'service'")
            services = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM communications")
            total_comms = cursor.fetchone()[0]
            conn.close()
            # Estimated revenue from completed bookings
            revenue = completed_bookings * 15000 + services * 1500
            return {
                "total_customers": total_customers,
                "today_bookings": today_bookings if today_bookings > 0 else pending_bookings,
                "pending_bookings": pending_bookings,
                "completed_bookings": completed_bookings,
                "test_rides": test_rides,
                "services": services,
                "total_communications": total_comms,
                "monthly_revenue": revenue,
                "revenue_formatted": f"₹{revenue/100000:.2f}L" if revenue >= 100000 else f"₹{revenue:,}"
            }
        except Exception as e:
            print(f"Error getting stats: {e}")
            return {"total_customers": 0, "today_bookings": 0, "pending_bookings": 0,
                    "completed_bookings": 0, "test_rides": 0, "services": 0,
                    "total_communications": 0, "monthly_revenue": 0, "revenue_formatted": "₹0"}

    def get_report_data(self) -> Dict:
        """Get analytics data for reports page"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            # Bookings by type
            cursor.execute("SELECT type, COUNT(*) FROM bookings GROUP BY type")
            bookings_by_type = {r[0]: r[1] for r in cursor.fetchall()}
            # Bookings by status
            cursor.execute("SELECT status, COUNT(*) FROM bookings GROUP BY status")
            bookings_by_status = {r[0]: r[1] for r in cursor.fetchall()}
            # Customers by status
            cursor.execute("SELECT status, COUNT(*) FROM customers GROUP BY status")
            customers_by_status = {r[0]: r[1] for r in cursor.fetchall()}
            # Top bikes
            cursor.execute("SELECT bike_model, COUNT(*) as cnt FROM bookings WHERE bike_model != '' GROUP BY bike_model ORDER BY cnt DESC LIMIT 5")
            top_bikes = [{"model": r[0], "count": r[1]} for r in cursor.fetchall()]
            # Monthly trends (last 6 months)
            monthly = []
            for i in range(5, -1, -1):
                d = datetime.now() - timedelta(days=30 * i)
                month_str = d.strftime("%Y-%m")
                cursor.execute("SELECT COUNT(*) FROM bookings WHERE created_date LIKE ?", (f"{month_str}%",))
                count = cursor.fetchone()[0]
                monthly.append({"month": d.strftime("%b %Y"), "bookings": count})
            # Customers by city
            cursor.execute("SELECT city, COUNT(*) as cnt FROM customers WHERE city != '' GROUP BY city ORDER BY cnt DESC LIMIT 10")
            by_city = [{"city": r[0], "count": r[1]} for r in cursor.fetchall()]
            conn.close()
            return {
                "bookings_by_type": bookings_by_type,
                "bookings_by_status": bookings_by_status,
                "customers_by_status": customers_by_status,
                "top_bikes": top_bikes,
                "monthly_trends": monthly,
                "customers_by_city": by_city
            }
        except Exception as e:
            print(f"Error getting report data: {e}")
            return {}

    def seed_sample_data(self):
        """Pre-populate sample data if tables are empty"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM customers")
            if cursor.fetchone()[0] > 0:
                conn.close()
                return
            # Sample customers
            sample_customers = [
                ("cust_001", "Rajesh Kumar", "9876543001", "rajesh@email.com", "Mumbai", '["Classic 350"]', "interested", "", "", "Interested in Royal Enfield"),
                ("cust_002", "Priya Sharma", "9876543002", "priya@email.com", "Delhi", '["Pulsar 220F"]', "booked_test_ride", "", "", "Booked test ride"),
                ("cust_003", "Amit Patel", "9876543003", "amit@email.com", "Ahmedabad", '["Dominar 400"]', "purchased", "", "", "Purchased Dominar"),
                ("cust_004", "Sneha Reddy", "9876543004", "sneha@email.com", "Hyderabad", '["Activa 6G"]', "new", "", "", "New lead"),
                ("cust_005", "Vikram Singh", "9876543005", "vikram@email.com", "Bangalore", '["Himalayan"]', "contacted", "", "", "Follow up needed"),
                ("cust_006", "Deepa Iyer", "9876543006", "deepa@email.com", "Chennai", '["Classic 350", "Himalayan"]', "interested", "", "", "Comparing models"),
                ("cust_007", "Arjun Nair", "9876543007", "arjun@email.com", "Kochi", '["Pulsar 220F"]', "booked_service", "", "", "Service due"),
                ("cust_008", "Kavita Joshi", "9876543008", "kavita@email.com", "Pune", '["Activa 6G"]', "purchased", "", "", "Repeat customer"),
                ("cust_009", "Rahul Verma", "9876543009", "rahul@email.com", "Kolkata", '["Dominar 400"]', "booked_test_ride", "", "", "Test ride scheduled"),
                ("cust_010", "Meera Das", "9876543010", "meera@email.com", "Jaipur", '["Classic 350"]', "interested", "", "", "Wants EMI details"),
                ("cust_011", "Suresh Babu", "9876543011", "suresh@email.com", "Coimbatore", '["Pulsar 220F"]', "purchased", "", "", "Referral from Arjun"),
                ("cust_012", "Anita Menon", "9876543012", "anita@email.com", "Mumbai", '["Himalayan"]', "new", "", "", "Inquired via website"),
            ]
            now = datetime.now()
            for i, c in enumerate(sample_customers):
                created = (now - timedelta(days=30 - i * 2)).isoformat()
                cursor.execute("INSERT INTO customers VALUES (?,?,?,?,?,?,?,?,?,?)",
                               (c[0], c[1], c[2], c[3], c[4], c[5], c[6], created, created, c[9]))
            # Sample bookings
            sample_bookings = [
                ("TR202603281430", "cust_002", "test_ride", "Pulsar 220F", "", "", "confirmed", "Preferred morning slot", ""),
                ("TR202603271000", "cust_009", "test_ride", "Dominar 400", "", "", "confirmed", "", ""),
                ("SV202603261500", "cust_007", "service", "Pulsar 220F", "Standard Service", "", "confirmed", "Chain lubrication needed", ""),
                ("TR202603251100", "cust_005", "test_ride", "Himalayan", "", "", "completed", "Customer impressed", ""),
                ("SV202603241400", "cust_003", "service", "Dominar 400", "Premium Service", "", "completed", "10K km service", ""),
                ("TR202603231600", "cust_006", "test_ride", "Classic 350", "", "", "completed", "", ""),
                ("SV202603221000", "cust_008", "service", "Activa 6G", "Basic Service", "", "completed", "Oil change", ""),
                ("TR202603211200", "cust_010", "test_ride", "Classic 350", "", "", "confirmed", "Wants weekend slot", ""),
                ("SV202603201300", "cust_011", "service", "Pulsar 220F", "Standard Service", "", "completed", "Brake pad replacement", ""),
                ("TR202603191500", "cust_001", "test_ride", "Classic 350", "", "", "cancelled", "Rescheduled", ""),
            ]
            for i, b in enumerate(sample_bookings):
                booking_date = (now - timedelta(days=i * 2)).strftime("%Y-%m-%d")
                created = (now - timedelta(days=i * 2 + 1)).isoformat()
                cursor.execute("INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?,?)",
                               (b[0], b[1], b[2], b[3], b[4], booking_date, b[6], b[7], created))
            # Sample communications
            sample_comms = [
                ("comm_001", "cust_002", "email", "Test Ride Confirmation", "Your test ride for Pulsar 220F is confirmed!", "", "sent"),
                ("comm_002", "cust_003", "sms", "", "Your service appointment is confirmed. Booking ID: SV202603241400", "", "delivered"),
                ("comm_003", "cust_001", "email", "Welcome to EveryLingua Motors", "Thank you for your interest! We have exciting offers.", "", "sent"),
                ("comm_004", "cust_005", "phone", "Follow-up Call", "Discussed Himalayan features. Customer interested.", "", "sent"),
                ("comm_005", "cust_006", "email", "Comparison: Classic 350 vs Himalayan", "Here is a detailed comparison of the two models.", "", "delivered"),
                ("comm_006", "cust_010", "sms", "", "Your EMI details for Classic 350: ₹5,200/month for 36 months.", "", "delivered"),
            ]
            for i, cm in enumerate(sample_comms):
                sent = (now - timedelta(days=i * 3)).isoformat()
                cursor.execute("INSERT INTO communications VALUES (?,?,?,?,?,?,?)",
                               (cm[0], cm[1], cm[2], cm[3], cm[4], sent, cm[6]))
            conn.commit()
            conn.close()
            print("✅ Sample CRM data seeded successfully")
        except Exception as e:
            print(f"Error seeding sample data: {e}")

    def get_settings(self) -> Dict:
        """Get dealership settings"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
            cursor.execute("SELECT key, value FROM settings")
            rows = cursor.fetchall()
            conn.close()
            settings = {r[0]: r[1] for r in rows}
            # Defaults
            defaults = {
                "dealership_name": "EveryLingua Motors",
                "address": "123 MG Road, Mumbai Central",
                "phone": "+91-9876543210",
                "email": "contact@everylingua.com",
                "working_hours": "9:00 AM - 8:00 PM",
                "notification_email": "true",
                "notification_sms": "true",
                "notification_booking": "true",
                "auto_followup": "true",
                "currency": "INR"
            }
            for k, v in defaults.items():
                if k not in settings:
                    settings[k] = v
            return settings
        except Exception as e:
            print(f"Error getting settings: {e}")
            return {}

    def update_settings(self, data: Dict) -> bool:
        """Update dealership settings"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("CREATE TABLE IF NOT EXISTS settings (key TEXT PRIMARY KEY, value TEXT)")
            for key, value in data.items():
                cursor.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, str(value)))
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error updating settings: {e}")
            return False

    def export_csv(self, data_type: str = "customers") -> str:
        """Export data as CSV string"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            if data_type == "customers":
                cursor.execute("SELECT id, name, phone, email, city, status, created_date, last_contact, notes FROM customers ORDER BY created_date DESC")
                headers = "ID,Name,Phone,Email,City,Status,Created Date,Last Contact,Notes"
            else:
                cursor.execute("""SELECT b.id, c.name, c.phone, b.type, b.bike_model, b.service_type,
                                  b.date, b.status, b.notes, b.created_date
                                  FROM bookings b LEFT JOIN customers c ON b.customer_id = c.id
                                  ORDER BY b.created_date DESC""")
                headers = "Booking ID,Customer,Phone,Type,Bike Model,Service Type,Date,Status,Notes,Created"
            rows = cursor.fetchall()
            conn.close()
            lines = [headers]
            for row in rows:
                lines.append(",".join([f'"{str(c).replace(chr(34), chr(34)+chr(34))}"' for c in row]))
            return "\n".join(lines)
        except Exception as e:
            print(f"Error exporting CSV: {e}")
            return ""


# Global CRM manager instance
crm_manager = CRMManager()
crm_manager.seed_sample_data()

def create_test_ride_booking(customer_name: str, phone: str, bike_model: str,
                           preferred_date: str, email: str = "", city: str = "") -> Dict:
    """Create test ride booking with CRM integration"""
    return crm_manager.create_test_ride_booking(customer_name, phone, bike_model, preferred_date, email, city)

def create_service_booking(customer_name: str, phone: str, bike_model: str,
                         service_type: str, preferred_date: str, email: str = "") -> Dict:
    """Create service booking with CRM integration"""
    return crm_manager.create_service_booking(customer_name, phone, bike_model, service_type, preferred_date, email)

def get_customer_dashboard(customer_id: str) -> Dict:
    """Get customer dashboard data"""
    return crm_manager.get_customer_dashboard_data(customer_id)
