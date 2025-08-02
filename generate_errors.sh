#!/bin/bash
set -e

echo "🔧 Running E-commerce App with Failure Configuration..."

# Load failure configuration
export $(cat config/failure.env | grep -v '^#' | xargs)

echo "📦 Installing Python dependencies..."
pip install -r app/requirements.txt

echo "🚀 Starting application (this will generate errors)..."

# Create logs directory if it doesn't exist
mkdir -p logs

cd app

# Start the application and capture logs
python main.py > ../logs/application.log 2>&1 &
APP_PID=$!

# Give the app a moment to start
sleep 2

echo "🧪 Testing endpoints to generate realistic errors..."

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

# Stop the application
echo "🛑 Stopping application..."
kill $APP_PID 2>/dev/null || true
wait $APP_PID 2>/dev/null || true

echo "✅ Error generation complete. Logs saved to logs/application.log"
