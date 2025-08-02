#!/bin/bash

echo "Testing AI-Powered Error Analysis Demo"
echo "========================================"

# Check if we're in the right directory
if [ ! -f "app/main.py" ]; then
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check if OpenAI API key is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "OPENAI_API_KEY not set. AI analysis will be skipped."
    echo "   Set it with: export OPENAI_API_KEY='your-api-key'"
    SKIP_AI=true
else
    echo "OpenAI API key configured"
    SKIP_AI=false
fi

echo ""
echo "Installing dependencies..."
pip install -q -r app/requirements.txt

echo ""
echo "Testing error generation..."
mkdir -p logs

# Load failure configuration
export $(cat config/failure.env | grep -v '^#' | xargs)

echo "Starting application with failure configuration..."
cd app

# Start the application in background and capture output
python main.py > ../logs/application.log 2>&1 &
APP_PID=$!

# Give it time to start and fail
sleep 3

echo "Testing API endpoints..."
# Test health endpoint
curl -s http://localhost:8000/health > /dev/null 2>&1 || echo "  Health check failed (expected)"

# Test registration
curl -s -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}' > /dev/null 2>&1 || echo "  Registration failed (expected)"

# Stop the application
kill $APP_PID 2>/dev/null || true
wait $APP_PID 2>/dev/null || true

cd ..

echo ""
echo "Log analysis:"
if [ -f "logs/application.log" ]; then
    LOG_LINES=$(wc -l < logs/application.log)
    echo "  Generated $LOG_LINES lines of application logs"
    echo ""
    echo "Sample log entries:"
    echo "  First 5 lines:"
    head -5 logs/application.log | sed 's/^/    /'
    echo "  ..."
    echo "  Last 5 lines:"
    tail -5 logs/application.log | sed 's/^/    /'
else
    echo "  No log file generated"
    exit 1
fi

if [ "$SKIP_AI" = false ]; then
    echo ""
    echo "Running AI analysis..."
    pip install -q embedchain openai requests beautifulsoup4 langdetect python-docx
    
    python scripts/error_analyzer.py
    
    echo ""
    echo "Analysis complete! Check the generated error_analysis_*.md file for detailed insights."
else
    echo ""
    echo "Skipping AI analysis (OpenAI API key not configured)"
fi

echo ""
echo "Demo completed successfully!"
echo ""
echo "What happened:"
echo "  1. Created a realistic e-commerce application"
echo "  2. Configured it to fail in multiple ways"
echo "  3. Generated authentic error logs"
if [ "$SKIP_AI" = false ]; then
    echo "  4. Analyzed errors with AI for expert insights"
else
    echo "  4. AI analysis skipped (configure OPENAI_API_KEY to enable)"
fi
echo ""
echo "Ready for CircleCI integration!"
