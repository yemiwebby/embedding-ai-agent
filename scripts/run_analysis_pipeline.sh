#!/bin/bash
set -e  # Exit immediately if a command fails

echo "🚀 AI-Powered Error Analysis Pipeline"
echo "===================================="

echo "📦 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

echo "⬆️ Installing dependencies..."
pip install --upgrade pip
pip install embedchain openai requests beautifulsoup4 langdetect python-docx

echo "📁 Creating logs directory..."
mkdir -p logs

echo "🔧 Generating realistic application errors..."
chmod +x generate_errors.sh
./generate_errors.sh

echo "📊 Verifying log file..."
if [ -f "logs/application.log" ]; then
    echo "✅ Log file generated successfully ($(wc -l < logs/application.log) lines)"
    echo "📄 Sample log entries:"
    head -10 logs/application.log
    echo "..."
    tail -5 logs/application.log
else
    echo "❌ No log file found, creating sample log for demonstration..."
    # Fallback to sample log if application failed to generate logs
    echo "[ERROR] $(date '+%Y-%m-%d %H:%M:%S') - Sample error for demonstration" > logs/application.log
fi

echo ""
echo "🤖 Running AI Error Analyzer..."
python scripts/error_analyzer.py

echo ""
echo "✅ Pipeline completed successfully!"
echo "📋 Check the generated error analysis report for insights."
