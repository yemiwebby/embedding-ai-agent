"""
E-commerce Demo Application with Intentional Failure Points
This application simulates a real-world e-commerce backend with common failure scenarios.
"""

import os
import logging
import time
import sqlite3
import requests
from datetime import datetime, timedelta
from flask import Flask, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from functools import wraps

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='[%(levelname)s] %(asctime)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration from environment variables
DATABASE_URL = os.getenv('DATABASE_URL', 'ecommerce.db')
JWT_SECRET = os.getenv('JWT_SECRET', 'your-secret-key')
PAYMENT_API_URL = os.getenv('PAYMENT_API_URL', 'https://api.payments.internal/v1')
EMAIL_API_URL = os.getenv('EMAIL_API_URL', 'https://api.notifications.internal/v1')
CACHE_URL = os.getenv('CACHE_URL', 'redis://localhost:6379')
API_KEY = os.getenv('API_KEY', 'default_api_key')
EVENT_BUS_URL = os.getenv('EVENT_BUS_URL', 'https://events.internal/api')

# Failure simulation flags
SIMULATE_DB_FAILURE = os.getenv('SIMULATE_DB_FAILURE', 'false').lower() == 'true'
SIMULATE_PAYMENT_TIMEOUT = os.getenv('SIMULATE_PAYMENT_TIMEOUT', 'false').lower() == 'true'
SIMULATE_AUTH_FAILURE = os.getenv('SIMULATE_AUTH_FAILURE', 'false').lower() == 'true'
SIMULATE_EMAIL_FAILURE = os.getenv('SIMULATE_EMAIL_FAILURE', 'false').lower() == 'true'
SIMULATE_MEMORY_LEAK = os.getenv('SIMULATE_MEMORY_LEAK', 'false').lower() == 'true'

class DatabaseError(Exception):
    pass

class PaymentError(Exception):
    pass

class AuthenticationError(Exception):
    pass

def init_database():
    """Initialize the database with required tables"""
    try:
        logger.info("Initializing database...")
        
        if SIMULATE_DB_FAILURE:
            # Simulate database connection failure
            logger.error("Database connection failed: Could not connect to database server")
            raise DatabaseError("Connection to database failed")
        
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        # Create users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create sessions table - but simulate missing table error
        if not SIMULATE_DB_FAILURE:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    token TEXT UNIQUE NOT NULL,
                    expires_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            ''')
        
        # Create orders table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                product_name TEXT NOT NULL,
                amount DECIMAL(10,2),
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise

def verify_token(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        
        if not token:
            logger.warning("Missing authorization token")
            return jsonify({'message': 'Token is missing'}), 401
        
        try:
            # Remove 'Bearer ' prefix if present
            if token.startswith('Bearer '):
                token = token[7:]
            
            if SIMULATE_AUTH_FAILURE:
                logger.error(f"AuthService: Invalid token detected, token={token[:20]}...")
                raise AuthenticationError("Invalid token")
            
            data = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
            current_user_id = data['user_id']
            
        except jwt.ExpiredSignatureError:
            logger.error("Token has expired")
            return jsonify({'message': 'Token has expired'}), 401
        except jwt.InvalidTokenError:
            logger.error(f"Invalid token detected: {token[:20]}...")
            return jsonify({'message': 'Token is invalid'}), 401
        except Exception as e:
            logger.error(f"Token verification failed: {str(e)}")
            return jsonify({'message': 'Token verification failed'}), 401
        
        return f(current_user_id, *args, **kwargs)
    return decorated

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        logger.info("Health check requested")
        
        # Check database connection
        conn = sqlite3.connect(DATABASE_URL)
        conn.close()
        
        # Simulate resource issues
        if SIMULATE_MEMORY_LEAK:
            # Simulate memory leak
            logger.warning("Memory usage high: 89% of available memory used")
            logger.warning("Disk usage warning: 91% used on /dev/sda1")
        
        logger.info("Health check passed")
        return jsonify({'status': 'healthy', 'timestamp': datetime.now().isoformat()})
        
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/register', methods=['POST'])
def register():
    """User registration endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        
        logger.info(f"Registration request received for user: {username}")
        
        if not all([username, email, password]):
            logger.warning("Registration failed: Missing required fields")
            return jsonify({'message': 'Missing required fields'}), 400
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Save to database
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)',
                (username, email, password_hash)
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            logger.info(f"User registered successfully: user_id={user_id}")
            return jsonify({'message': 'User registered successfully', 'user_id': user_id})
            
        except sqlite3.IntegrityError:
            logger.error(f"Registration failed: Username or email already exists")
            return jsonify({'message': 'Username or email already exists'}), 409
        finally:
            conn.close()
            
    except Exception as e:
        logger.error(f"Registration error: {str(e)}")
        return jsonify({'message': 'Registration failed'}), 500

@app.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        username = data.get('username')
        password = data.get('password')
        
        logger.info(f"Login request received: username={username}")
        
        if not all([username, password]):
            return jsonify({'message': 'Missing credentials'}), 400
        
        # Get user from database
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute('SELECT id, password_hash FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if not user or not check_password_hash(user[1], password):
            logger.warning(f"Login failed: Invalid credentials for user {username}")
            return jsonify({'message': 'Invalid credentials'}), 401
        
        user_id = user[0]
        
        # Create JWT token
        token = jwt.encode({
            'user_id': user_id,
            'exp': datetime.utcnow() + timedelta(hours=24)
        }, JWT_SECRET, algorithm='HS256')
        
        # Try to save session (this might fail if sessions table doesn't exist)
        try:
            cursor.execute(
                'INSERT INTO sessions (user_id, token, expires_at) VALUES (?, ?, ?)',
                (user_id, token, datetime.utcnow() + timedelta(hours=24))
            )
            conn.commit()
        except sqlite3.OperationalError as e:
            logger.error(f"Database query failed: ERROR: relation \"sessions\" does not exist")
            logger.error(f"    at sqlite3.connect.execute(session_insert)")
            logger.error(f"    at app.login(main.py:180)")
            # Continue without saving session
        
        conn.close()
        
        logger.info(f"User logged in successfully: user_id={user_id}")
        return jsonify({'token': token, 'user_id': user_id})
        
    except Exception as e:
        logger.error(f"Login error: {str(e)}")
        return jsonify({'message': 'Login failed'}), 500

@app.route('/order', methods=['POST'])
@verify_token
def create_order(current_user_id):
    """Create a new order"""
    try:
        data = request.get_json()
        product_name = data.get('product_name')
        amount = data.get('amount')
        
        logger.info(f"Order creation request: user_id={current_user_id}, product={product_name}")
        
        if not all([product_name, amount]):
            return jsonify({'message': 'Missing order details'}), 400
        
        # Save order to database
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute(
            'INSERT INTO orders (user_id, product_name, amount) VALUES (?, ?, ?)',
            (current_user_id, product_name, amount)
        )
        order_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        # Process payment
        try:
            payment_result = process_payment(order_id, amount)
            
            if payment_result['status'] == 'success':
                logger.info(f"Order completed successfully: order_id={order_id}")
                return jsonify({
                    'message': 'Order created successfully',
                    'order_id': order_id,
                    'payment_status': 'completed'
                })
            else:
                logger.error(f"Payment failed for order {order_id}: {payment_result['error']}")
                return jsonify({
                    'message': 'Order created but payment failed',
                    'order_id': order_id,
                    'payment_status': 'failed'
                }), 402
                
        except PaymentError as e:
            logger.error(f"Payment processing failed: {str(e)}")
            return jsonify({
                'message': 'Order created but payment failed',
                'order_id': order_id,
                'payment_status': 'failed'
            }), 402
            
    except Exception as e:
        logger.error(f"Order creation failed: {str(e)}")
        return jsonify({'message': 'Order creation failed'}), 500

def process_payment(order_id, amount):
    """Process payment through external payment service"""
    try:
        logger.info(f"Processing payment for order {order_id}: amount=${amount}")
        
        # Simulate payment service timeout
        if SIMULATE_PAYMENT_TIMEOUT:
            logger.info(f"Calling payment service: POST {PAYMENT_API_URL}/process")
            time.sleep(6)  # Simulate long response time
            logger.error(f"Timeout while calling payment-service: POST {PAYMENT_API_URL}/process - took 6000ms")
            raise PaymentError("Payment service timeout")
        
        # Simulate payment gateway call
        try:
            payment_data = {
                'order_id': order_id,
                'amount': amount,
                'currency': 'USD'
            }
            
            # This will fail due to invalid URL
            response = requests.post(
                f"{PAYMENT_API_URL}/process",
                json=payment_data,
                timeout=5
            )
            
            if response.status_code == 200:
                return {'status': 'success', 'transaction_id': f"txn_{order_id}"}
            else:
                logger.error(f"Payment gateway returned {response.status_code}: \"Transaction declined by provider\"")
                return {'status': 'failed', 'error': 'Transaction declined'}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Payment service connection failed: {str(e)}")
            
            # Simulate retry logic
            logger.info(f"Retrying payment request for order_id={order_id}")
            logger.info("Retry attempt 1/3")
            
            # Second attempt also fails
            logger.error("Payment gateway returned 500: \"Transaction declined by provider\"")
            
            # Simulate NullPointerException in payment processing
            logger.error("java.lang.NullPointerException")
            logger.error("    at com.ecommerce.payment.PaymentProcessor.process(PaymentProcessor.java:142)")
            logger.error("    at com.ecommerce.billing.BillingService.chargeUser(BillingService.java:85)")
            
            raise PaymentError("Payment processing failed after retries")
            
    except Exception as e:
        logger.error(f"Payment processing error: {str(e)}")
        raise PaymentError(str(e))

@app.route('/logout', methods=['POST'])
@verify_token
def logout(current_user_id):
    """User logout endpoint"""
    try:
        logger.info(f"Logout request received: user_id={current_user_id}")
        
        # Try to send logout event to event bus
        try:
            event_data = {
                'event_type': 'user_logout',
                'user_id': current_user_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # This will fail due to wrong configuration
            response = requests.post(
                f'{EVENT_BUS_URL}/events',
                json=event_data,
                timeout=2
            )
            
        except requests.exceptions.ConnectionError:
            logger.error("Failed to send logout event to event-bus: ConnectionRefusedError [Errno 111]")
            # Continue with logout even if event bus fails
        
        logger.info(f"User logged out successfully: user_id={current_user_id}")
        return jsonify({'message': 'Logged out successfully'})
        
    except Exception as e:
        logger.error(f"Logout error: {str(e)}")
        return jsonify({'message': 'Logout failed'}), 500

@app.route('/send-notification', methods=['POST'])
@verify_token
def send_notification(current_user_id):
    """Send email notification to user"""
    try:
        data = request.get_json()
        email = data.get('email')
        message = data.get('message')
        
        logger.info(f"Sending notification to {email}")
        
        if SIMULATE_EMAIL_FAILURE:
            logger.error("SMTP server not responding: [Errno 110] Connection timed out")
            logger.error(f"Failed to send notification email to {email}")
            return jsonify({'message': 'Failed to send notification'}), 500
        
        # Simulate successful email sending
        logger.info(f"Notification sent successfully to {email}")
        return jsonify({'message': 'Notification sent successfully'})
        
    except Exception as e:
        logger.error(f"Notification sending failed: {str(e)}")
        return jsonify({'message': 'Failed to send notification'}), 500

@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({'message': 'Internal server error'}), 500

@app.errorhandler(404)
def not_found(error):
    logger.warning(f"Endpoint not found: {request.path}")
    return jsonify({'message': 'Endpoint not found'}), 404

def cleanup_sessions():
    """Clean up expired sessions"""
    try:
        logger.info("Session cleanup job started")
        
        conn = sqlite3.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM sessions WHERE expires_at < ?', (datetime.utcnow(),))
        deleted_count = cursor.rowcount
        
        conn.commit()
        conn.close()
        
        logger.info(f"Session cleanup completed: removed {deleted_count} expired sessions")
        
    except Exception as e:
        logger.error(f"Session cleanup failed: {str(e)}")

if __name__ == '__main__':
    try:
        logger.info("Starting e-commerce backend server on port 8000")
        
        # Initialize database
        init_database()
        
        # Perform cleanup
        cleanup_sessions()
        
        # Check if we should simulate critical failure
        if os.getenv('SIMULATE_CRITICAL_FAILURE', 'false').lower() == 'true':
            logger.info("Shutting down gracefully...")
            logger.critical("Unhandled exception in main thread")
            logger.critical("Traceback (most recent call last):")
            logger.critical('  File "main.py", line 400, in <module>')
            logger.critical("    app.run()")
            logger.critical('  File "main.py", line 398, in run_app')
            logger.critical("    initialize_services()")
            logger.critical('  File "services/initializer.py", line 33, in initialize_services')
            logger.critical('    raise RuntimeError("Unable to initialize critical service: payment-service")')
            logger.critical('RuntimeError: Unable to initialize critical service: payment-service')
            raise RuntimeError("Unable to initialize critical service: payment-service")
        
        app.run(host='0.0.0.0', port=8000, debug=False)
        
    except Exception as e:
        logger.critical(f"Failed to start application: {str(e)}")
        raise
