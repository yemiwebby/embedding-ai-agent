#!/bin/bash
set -e

echo "🔧 Running E-commerce App with Failure Configuration..."

# Load failure configuration
export $(cat config/failure.env | grep -v '^#' | xargs)

echo "📦 Installing Python dependencies..."
pip install -r app/requirements.txt

echo "🚀 Starting application (this will generate errors)..."

# Create logs directory if it doesn't exist
echo "📁 Creating logs directory..."
mkdir -p logs
echo "✅ logs directory created: $(ls -ld logs)"

cd app
echo "📁 Changed to app directory: $(pwd)"

# Start the application and capture logs
echo "🔄 Starting Python application and capturing logs..."
python main.py > ../logs/application.log 2>&1 &
APP_PID=$!
echo "🔄 Application started with PID: $APP_PID"

# Give the app a moment to start
sleep 2

echo "🧪 Testing endpoints to generate realistic errors..."

# Check if the app is still running (it might have crashed on startup)
if kill -0 $APP_PID 2>/dev/null; then
    echo "✅ App is running, testing HTTP endpoints..."
    
    # Test health check
    echo "Testing health endpoint..."
    curl -s http://localhost:8000/health || echo "Health check failed as expected"

    # Test user registration
    echo "Testing user registration..."
    curl -s -X POST http://localhost:8000/register \
      -H "Content-Type: application/json" \
      -d '{"username":"testuser","email":"test@example.com","password":"password123"}' || echo "Registration failed as expected"

    # Test login (this will fail due to auth issues)
    echo "Testing login..."
    curl -s -X POST http://localhost:8000/login \
      -H "Content-Type: application/json" \
      -d '{"username":"testuser","password":"password123"}' || echo "Login failed as expected"

    # Test order creation (will fail due to auth)
    echo "Testing order creation..."
    curl -s -X POST http://localhost:8000/order \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer invalid-token" \
      -d '{"product_name":"Laptop","amount":999.99}' || echo "Order creation failed as expected"
      
    # Wait a bit more for logs to accumulate
    sleep 3
else
    echo "⚠️  App crashed during startup (simulated critical failure)"
    echo "This generates realistic startup failure logs for analysis"
    sleep 2
fi

# Stop the application
echo "🛑 Stopping application..."
kill $APP_PID 2>/dev/null || true
wait $APP_PID 2>/dev/null || true

# Ensure we have some log content for analysis
echo "🔍 Checking log file status..."
if [ ! -f "../logs/application.log" ] || [ ! -s "../logs/application.log" ]; then
    echo "⚠️  No application logs generated. Creating sample error logs for demonstration..."
    cd .. # Make sure we're in the root directory
    mkdir -p logs # Ensure logs directory exists
    cat > logs/application.log << 'EOF'
[CRITICAL] 2024-08-02 12:34:56 - Failed to start application: Unable to initialize critical service: payment-service
[ERROR] 2024-08-02 12:34:56 - Database connection failed: could not connect to server: Connection refused
[ERROR] 2024-08-02 12:34:56 - Service 'payment-service' is not responding on port 8080
[WARNING] 2024-08-02 12:34:56 - Retrying database connection (attempt 1/3)
[ERROR] 2024-08-02 12:34:57 - Database connection failed: could not connect to server: Connection refused
[WARNING] 2024-08-02 12:34:57 - Retrying database connection (attempt 2/3)
[ERROR] 2024-08-02 12:34:58 - Database connection failed: could not connect to server: Connection refused
[WARNING] 2024-08-02 12:34:58 - Retrying database connection (attempt 3/3)
[CRITICAL] 2024-08-02 12:34:59 - Unable to initialize critical service: payment-service
[ERROR] 2024-08-02 12:34:59 - RuntimeError: Unable to initialize critical service: payment-service
EOF
    echo "✅ Sample logs created: $(wc -l < logs/application.log) lines"
else
    cd .. # Make sure we're in the root directory
    echo "✅ Application logs found: $(wc -l < logs/application.log) lines"
fi

echo "✅ Error generation complete. Logs saved to logs/application.log"
