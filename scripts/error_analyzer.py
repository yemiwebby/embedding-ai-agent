"""
AI-Powered Error Log Analyzer for CI/CD Pipelines
This script uses Embedchain to analyze error logs and provide intelligent insights.
"""

import os
import sys
from datetime import datetime
from embedchain import App

# Check for OpenAI API key
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    print("❌ Error: OPENAI_API_KEY environment variable is not set!")
    print("   Please set your OpenAI API key:")
    print("   export OPENAI_API_KEY='your-api-key-here'")
    exit(1)

# Set the API key for embedchain
os.environ["OPENAI_API_KEY"] = openai_api_key

def analyze_error_logs(log_file_path="logs/application.log"):
    """
    Analyze error logs using AI and generate a comprehensive summary
    """
    try:
        # Initialize Embedchain app
        app = App()
        
        # Debug: Check current working directory and list files
        current_dir = os.getcwd()
        print(f"🔍 Current working directory: {current_dir}")
        print(f"🔍 Looking for log file at: {os.path.abspath(log_file_path)}")
        
        # List contents of logs directory if it exists
        logs_dir = os.path.dirname(log_file_path) or "."
        if os.path.exists(logs_dir):
            print(f"📁 Contents of {logs_dir}:")
            for item in os.listdir(logs_dir):
                item_path = os.path.join(logs_dir, item)
                if os.path.isfile(item_path):
                    size = os.path.getsize(item_path)
                    print(f"   📄 {item} ({size} bytes)")
                else:
                    print(f"   📁 {item}/")
        else:
            print(f"❌ Directory {logs_dir} does not exist")
        
        # Read the log file
        if not os.path.exists(log_file_path):
            print(f"❌ Error: Log file {log_file_path} not found")
            return False
            
        with open(log_file_path, "r") as f:
            logs = f.read()
        
        if not logs.strip():
            print("❌ Error: Log file is empty")
            return False
        
        print(f"📖 Analyzing {len(logs)} characters of log data...")
        
        # Enhanced prompt for better analysis
        prompt = f"""You are an expert DevOps engineer and log analyst. Analyze the following application error log and provide a comprehensive summary.

Please structure your analysis as follows:

## 🔍 Executive Summary
Provide a brief overview of the main issues found.

## 🚨 Critical Issues
List the most severe problems that need immediate attention, including:
- Critical failures that prevent the application from starting
- Security-related issues
- Data loss risks

## ⚠️ Major Issues  
Identify significant problems that impact functionality:
- Service failures and timeouts
- Database connection issues
- Authentication problems
- Payment processing failures

## 📊 Error Patterns & Statistics
Analyze patterns in the errors:
- Most frequent error types
- Time-based patterns
- Cascading failures
- Retry attempts and their success rates

## 🛠️ Recommended Actions
Provide specific, actionable recommendations:
- Immediate fixes required
- Configuration changes needed
- Infrastructure improvements
- Monitoring enhancements

## 💡 Root Cause Analysis
Identify the underlying causes of the issues and their relationships.

---

Application Log Data:
{logs}

Please provide detailed, actionable insights that would help a development team quickly understand and resolve these issues."""

        # Query the AI model
        print("🤖 Generating AI analysis...")
        result = app.query(prompt)
        
        # Save the analysis
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = f"error_analysis_{timestamp}.md"
        
        with open(output_file, "w") as f:
            f.write(f"# AI Error Log Analysis Report\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"**Log File:** {log_file_path}\n")
            f.write(f"**Analysis Tool:** Embedchain AI Agent\n\n")
            f.write("---\n\n")
            f.write(result)
        
        print(f"✅ Analysis complete! Report saved to: {output_file}")
        
        # Also display the analysis
        print("\n" + "="*60)
        print("🧠 AI-GENERATED ERROR ANALYSIS")
        print("="*60)
        print(result)
        print("="*60)
        
        return True
        
    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return False

def main():
    """Main function to run the error analysis"""
    print("🚀 Starting AI-powered error log analysis...")
    
    # Check if OpenAI API key is set
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please set your OpenAI API key before running this script")
        sys.exit(1)
    
    # Analyze the logs
    success = analyze_error_logs()
    
    if success:
        print("\n✅ Error analysis completed successfully!")
        print("📋 The AI has provided actionable insights to help resolve the issues.")
    else:
        print("\n❌ Error analysis failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
