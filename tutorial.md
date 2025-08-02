# Embedding AI Agents into CI/CD Pipelines with embedchain

Every developer knows the sequence: a deployment fails, alerts starts firing, and you are staring at error logs stretching hundreds of lines - trying to piece together what went wrong. While CI/CD automated builds and deployment make for a more efficient means of upgrading software, in the event of a failure, one can be left drowning in data without any intelligence. The question then is: What if your pipelines could not only detect failures, but actually understand them. What if it could analyz## Testing the Complete System

Before running the full pipeline, you can test the system locally:

1. **Test Error Generation**:

   ```bash
   cd circle_ci_agent_demo
   ./generate_errors.sh
   ```

2. **Test AI Analysis**:

   ```bash
   export OPENAI_API_KEY="your-api-key"
   python scripts/error_analyzer.py
   ```

3. **Run Complete Pipeline**:
   ```bash
   ./scripts/run_analysis_pipeline.sh
   ```

Run the CircleCI pipeline once the configuration is complete. The pipeline will:

1. **Deploy** your e-commerce application with failure configuration
2. **Generate** realistic errors through API testing
3. **Capture** authentic application logs
4. **Analyze** the errors with AI to provide expert insights
5. **Display** actionable recommendations

## Sample AI Analysis Output

When the pipeline runs successfully, you'll see intelligent analysis like this:

```
🔍 Executive Summary
The application experienced multiple critical failures during startup and operation,
including database connectivity issues, payment service timeouts, and authentication
problems that prevented normal operation.

🚨 Critical Issues
- Database initialization failure: Missing 'sessions' table
- Payment service completely unreachable
- Critical service initialization failure preventing startup

⚠️ Major Issues
- Authentication token validation failing
- Email service connectivity problems
- Resource warnings (disk space, memory)

🛠️ Recommended Actions
1. Verify database schema and run migrations
2. Check payment service configuration and network connectivity
3. Validate JWT secret key configuration
4. Review infrastructure resource allocation
```

## Conclusion

You have successfully transformed a traditional CI/CD pipeline into an intelligent system that doesn't just detect failures but truly understands them. By building a realistic e-commerce application with authentic failure modes, you've created a system that:

- **Generates Real Errors**: Authentic failure patterns from actual application code
- **Provides Expert Analysis**: AI-powered insights that match senior developer expertise
- **Delivers Actionable Results**: Specific recommendations rather than generic summaries
- **Scales Automatically**: Processes any volume of logs instantly
- **Learns Continuously**: Improves analysis quality over time

The AI agent you built combines the power of EmbedChain's RAG capabilities with the reliability of CircleCI's automation, creating a solution that automatically processes complex error logs and delivers expert-level insights in minutes rather than hours. What once required senior developers to manually parse through voluminous log files, correlate errors, and identify root cause patterns now happens automatically with every pipeline run.

This approach not only saves countless hours of debugging time but also ensures that critical issues are identified and understood immediately, allowing your team to focus on implementing solutions rather than hunting for problems. The realistic error scenarios prepare you for actual production issues, making this not just a technical demonstration but a practical learning experience for handling real-world failures.terns, identify root causes and present actionable insights automatically.

This is what can be achieved by embedding AI Agents into your CI/CD Pipeline using Embedchain. In this this tutorial, I’ll walk you through building an intelligent error analysis agent that transforms your debugging workflow from hours of manual log parsing into instant AI-powered insights

## Prerequisites

To follow through this tutorial you will need:

**Required:**

- An OpenAI API Key (free tier available)
- A CircleCI account (free tier available)
- A GitHub account (free)
- Basic understanding of Python programming

**That's it!** No external service accounts needed - we'll simulate everything locally.

To demonstrate the AI Agent capabilities, you need realistic data that mirrors what actually occurs in production. Instead of using fake logs, you'll build a real e-commerce application that intentionally generates authentic errors when deployed with broken configurations.

This approach provides several advantages:

- **Authentic error patterns**: Real stack traces, proper timestamps, and genuine failure cascades
- **Realistic complexity**: Multiple interconnected services with dependencies
- **Configurable failure modes**: Environment-driven error simulation
- **Educational value**: Learn about common production issues by seeing them happen

Your sample application will generate errors including:

- Database connection failures and missing tables
- Service timeout errors and payment processing failures
- Authentication problems and token validation issues
- Infrastructure warnings and resource exhaustion
- Critical service crashes and initialization failures

In this tutorial, your AI Agent will act as an expert DevOps engineer, analyzing these real application logs and providing comprehensive insights including root cause analysis, error patterns, and actionable recommendations.

## Building the Realistic Error-Generating Application

Start by creating the project structure. Create a new folder named `circle_ci_agent_demo` and navigate into it:

```bash
mkdir circle_ci_agent_demo && cd circle_ci_agent_demo
```

### 1. Create the E-commerce Application

First, create the application directory structure:

```bash
mkdir -p app config scripts .circleci
```

Create the main Flask application in `app/main.py`. This will be a realistic e-commerce backend with multiple failure points:

````
```python
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
PAYMENT_SERVICE_URL = os.getenv('PAYMENT_SERVICE_URL', 'http://payment-gateway.invalid')
EMAIL_SERVICE_URL = os.getenv('EMAIL_SERVICE_URL', 'http://email-service.invalid')

# Failure simulation flags
SIMULATE_DB_FAILURE = os.getenv('SIMULATE_DB_FAILURE', 'false').lower() == 'true'
SIMULATE_PAYMENT_TIMEOUT = os.getenv('SIMULATE_PAYMENT_TIMEOUT', 'false').lower() == 'true'
SIMULATE_AUTH_FAILURE = os.getenv('SIMULATE_AUTH_FAILURE', 'false').lower() == 'true'
SIMULATE_EMAIL_FAILURE = os.getenv('SIMULATE_EMAIL_FAILURE', 'false').lower() == 'true'
SIMULATE_CRITICAL_FAILURE = os.getenv('SIMULATE_CRITICAL_FAILURE', 'false').lower() == 'true'

# ... (Application code with endpoints like /health, /login, /order, etc.)
# This creates realistic errors when failure flags are enabled

if __name__ == '__main__':
    try:
        logger.info("Starting e-commerce backend server on port 8000")

        # Initialize database
        init_database()

        # Check if we should simulate critical failure
        if SIMULATE_CRITICAL_FAILURE:
            logger.critical("Unable to initialize critical service: payment-service")
            raise RuntimeError("Unable to initialize critical service: payment-service")

        app.run(host='0.0.0.0', port=8000, debug=False)

    except Exception as e:
        logger.critical(f"Failed to start application: {str(e)}")
        raise
````

This application includes:

- **User authentication** with JWT tokens
- **Database operations** with SQLite
- **Payment processing** simulation
- **Email notifications**
- **Configurable failure modes** via environment variables

Create the requirements file in `app/requirements.txt`:

```
flask==2.3.3
requests==2.31.0
PyJWT==2.8.0
Werkzeug==2.3.7
```

### 2. Create Configuration Files

Create two configuration files to control the application behavior:

**Success Configuration** (`config/success.env`):

```bash
# Working Configuration - Simplified
DATABASE_URL=ecommerce.db
JWT_SECRET=super-secure-jwt-secret-key-for-production
PAYMENT_API_URL=https://api.payments.internal/v1
EMAIL_API_URL=https://api.notifications.internal/v1
CACHE_URL=redis://cache.internal:6379
API_KEY=prod_key_12345_valid

# Failure simulation flags (disabled)
SIMULATE_DB_FAILURE=false
SIMULATE_PAYMENT_TIMEOUT=false
SIMULATE_AUTH_FAILURE=false
SIMULATE_EMAIL_FAILURE=false
SIMULATE_CRITICAL_FAILURE=false
```

**Failure Configuration** (`config/failure.env`):

```bash
# Failure Configuration - Simulated Issues
# Wrong environment configurations (no real services needed)
DATABASE_URL=postgres://user:pass@db.staging:5432/ecommerce  # Staging DB in prod
JWT_SECRET=dev-secret-not-for-prod  # Development secret in production
PAYMENT_API_URL=https://api.payments.internal/v0  # Wrong API version
EMAIL_API_URL=http://notifications.staging:8080  # HTTP instead of HTTPS + wrong env
CACHE_URL=redis://cache.staging:6379  # Wrong environment
API_KEY=expired_key_12345  # Expired API key

# Failure simulation flags (enabled for demonstration)
SIMULATE_DB_FAILURE=true
SIMULATE_PAYMENT_TIMEOUT=true
SIMULATE_AUTH_FAILURE=true
SIMULATE_EMAIL_FAILURE=true
SIMULATE_CRITICAL_FAILURE=true
```

### 3. Create Error Generation Script

Create `generate_errors.sh` to run the application with failure configuration and generate realistic errors:

```bash
#!/bin/bash
set -e

echo "🔧 Running E-commerce App with Failure Configuration..."

# Load failure configuration
export $(cat config/failure.env | grep -v '^#' | xargs)

echo "📦 Installing Python dependencies..."
pip install -r app/requirements.txt

echo "🚀 Starting application (this will generate errors)..."
cd app

# Start the application and capture logs
python main.py > ../logs/application.log 2>&1 &
APP_PID=$!

# Give the app a moment to start
sleep 2

echo "🧪 Testing endpoints to generate realistic errors..."

# Test various endpoints to trigger different types of failures
curl -s http://localhost:8000/health || echo "Health check failed as expected"
curl -s -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}' || echo "Registration failed"

# More API tests...

# Stop the application
kill $APP_PID 2>/dev/null || true

echo "✅ Error generation complete. Logs saved to logs/application.log"
```

Make the script executable:

```bash
chmod +x generate_errors.sh
```

## Creating the AI Error Analyzer

Now, create the AI-powered error analyzer that will process these realistic logs. Create `scripts/error_analyzer.py`:

````python

```python
"""
AI-Powered Error Log Analyzer for CI/CD Pipelines
This script uses Embedchain to analyze error logs and provide intelligent insights.
"""

import os
import sys
from datetime import datetime
from embedchain import App

# Set your OpenAI API key
os.environ["OPENAI_API_KEY"] = os.getenv("OPENAI_API_KEY")

def analyze_error_logs(log_file_path="logs/application.log"):
    """
    Analyze error logs using AI and generate a comprehensive summary
    """
    try:
        # Initialize Embedchain app
        app = App()

        # Read the log file
        with open(log_file_path, "r") as f:
            logs = f.read()

        print(f"📖 Analyzing {len(logs)} characters of log data...")

        # Enhanced prompt for comprehensive analysis
        prompt = f"""You are an expert DevOps engineer and log analyst. Analyze the following application error log and provide a comprehensive summary.

Please structure your analysis as follows:

## 🔍 Executive Summary
Provide a brief overview of the main issues found.

## 🚨 Critical Issues
List the most severe problems that need immediate attention:
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
            f.write(f"**Log File:** {log_file_path}\n\n")
            f.write("---\n\n")
            f.write(result)

        print(f"✅ Analysis complete! Report saved to: {output_file}")
        return True

    except Exception as e:
        print(f"❌ Error during analysis: {str(e)}")
        return False

if __name__ == "__main__":
    analyze_error_logs()
````

This enhanced error analyzer:

- Reads the real application logs generated by your e-commerce app
- Uses a comprehensive prompt for structured analysis
- Provides actionable insights including root cause analysis
- Saves timestamped reports for historical tracking

## Pipeline Automation Script

Create `scripts/run_analysis_pipeline.sh` to automate the entire process:

```bash
#!/bin/bash
set -e  # Exit immediately if a command fails

echo "� AI-Powered Error Analysis Pipeline"
echo "===================================="

echo "�📦 Setting up Python environment..."
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
fi

echo ""
echo "🤖 Running AI Error Analyzer..."
python scripts/error_analyzer.py

echo ""
echo "✅ Pipeline completed successfully!"
echo "📋 Check the generated error analysis report for insights."
```

Make this script executable:

```bash
chmod +x scripts/run_analysis_pipeline.sh
```

## Setting Up the CircleCI Pipeline

With the realistic application and AI analyzer ready, create the CircleCI configuration. Create `.circleci/config.yml`:

```yaml
version: 2.1

executors:
  python-executor:
    docker:
      - image: cimg/python:3.10

jobs:
  deploy-and-analyze:
    executor: python-executor
    steps:
      - checkout

      - run:
          name: Verify Environment
          command: |
            echo "✅ Environment check:"
            echo "- Python version: $(python3 --version)"
            echo "- Working directory: $(pwd)"
            echo "- OPENAI_API_KEY configured: ${OPENAI_API_KEY:+Yes}${OPENAI_API_KEY:-No}"

      - run:
          name: Deploy Application (Simulate Deployment)
          command: |
            echo "🚀 Simulating application deployment..."
            echo "📦 Installing application dependencies..."
            pip install -r app/requirements.txt
            echo "✅ Application deployment completed"

      - run:
          name: Run Application Health Checks
          command: |
            echo "🔍 Running application health checks..."
            echo "⚠️  This will intentionally generate errors for demonstration"

            # Make scripts executable
            chmod +x generate_errors.sh
            chmod +x scripts/run_analysis_pipeline.sh

            # Generate realistic errors by running the application
            echo "📝 Generating application logs with realistic errors..."
            ./generate_errors.sh || echo "Expected failures occurred during health checks"

      - run:
          name: AI-Powered Error Analysis
          command: |
            echo "🤖 Starting AI-powered error analysis..."
            echo "📊 This is where the magic happens - AI analyzes the errors!"

            # Set up environment for AI analysis
            python3 -m venv analysis_env
            source analysis_env/bin/activate
            pip install --upgrade pip
            pip install embedchain openai requests beautifulsoup4 langdetect python-docx

            # Run the AI error analyzer
            python scripts/error_analyzer.py

      - run:
          name: Display Analysis Results
          command: |
            echo "📋 AI Analysis Results:"
            echo "======================"

            # Find the most recent analysis file
            ANALYSIS_FILE=$(ls -t error_analysis_*.md 2>/dev/null | head -1)

            if [ -n "$ANALYSIS_FILE" ]; then
              echo "📄 Displaying AI analysis from: $ANALYSIS_FILE"
              echo ""
              cat "$ANALYSIS_FILE"
            else
              echo "⚠️  No analysis file found. Checking for logs..."
              if [ -f "logs/application.log" ]; then
                echo "📝 Raw application logs:"
                cat logs/application.log
              else
                echo "❌ No logs or analysis found"
              fi
            fi

      - store_artifacts:
          path: /tmp/analysis-results
          destination: ai-analysis-results

workflows:
  deploy-and-analyze-errors:
    jobs:
      - deploy-and-analyze:
          context:
            - ai-error-analysis # Context containing OPENAI_API_KEY
```

This enhanced pipeline:

- **Deploys the real application** with failure configuration
- **Runs health checks** that trigger authentic errors
- **Captures real logs** from the application failure
- **Analyzes with AI** to provide expert-level insights
- **Displays results** directly in the pipeline output
- **Archives artifacts** for later review

# **Connecting the Realistic Application to CircleCI**

```bash
chmod +x run_summary_generator.sh
```

With the AI Agent and environment setup ready, it’s time to set up your pipeline in CircleCI. The pipeline will take the following steps:

- Prepare the error log data
- Set up the python environment securely
- Execute our AI Agent
- Display the intelligence analysis

To create the pipeline, create a new folder named `.circleci` in your project. In this folder, create a new file named `config.yml` and add the following code to it.

```
version: 2.1

executors:
  python-executor:
    docker:
      - image: cimg/python:3.10  # CircleCI official Python image

jobs:
  run-ai-summarizer:
    executor: python-executor
    steps:
      - checkout

      - run:
          name: Show Environment (for debugging)
          command: |
            echo "✅ OPENAI_API_KEY starts with: ${OPENAI_API_KEY:0:8}"

      - run:
          name: Prepare Error Log File
          command: |
            echo "📝 Preparing error log file..."
            cp sample_error_log.txt error_log.txt

      - run:
          name: Run AI Summarizer Script
          command: |
            echo "🤖 Running AI summarizer..."
            ./run_summary_generator.sh

      - run:
          name: Display AI Summary
          command: |
            echo "===== 🧠 AI-Generated Summary ====="
            cat error_summary.md
            echo "==================================="

workflows:
  run-ai-agent:
    jobs:
      - run-ai-summarizer
```

# **Connecting the application to CircleCI**

The next step is to set up a repository on GitHub and link the project to CircleCI. Review [Pushing a project to GitHub](https://circleci.com/blog/pushing-a-project-to-github/) for instructions.

Log in to your CircleCI account. If you signed up with your GitHub account, all your repositories will be available on your project’s dashboard.

Click **Set Up Project** next to your `circle_ci_agent_demo` project.

![](https://miro.medium.com/v2/resize:fit:1400/1*xsgrfW3SMEP5XS8O32yGVg.png)

You will be prompted to enter the name of the branch where your code is housed on GitHub. Click **Set Up Project** once you are done.

![](https://miro.medium.com/v2/resize:fit:1400/1*ZVPUIUe4FfIF6k6L7pgX7Q.png)

Once this project has been setup, the next thing to do is to create an environment variable for your OpenAI API key. To do this, go to **Project settings**, click on **environment variables** and add a new environment variable named `OPENAI_API_KEY`

![](https://miro.medium.com/v2/resize:fit:1400/1*jEe8gdIpu-wBEvArtIPAxg.png)

Ensure the name used matches with the one in your `config.yml` and `error_summary_agent.py` file for consistency sake and to avoid pipeline build failing.

Run the pipeline once the configuration is complete.

![](https://miro.medium.com/v2/resize:fit:1400/1*FYeVzA5qG5TltqKsu8tRBA.png)

The build was successful, with the analysis generated below.

![image.png](attachment:eebb8fd9-ad0f-403e-89c5-a156d80741b3:image.png)

## Conclusion

You have successfully transformed a traditional CI/CD pipeline into an intelligent system that doesn’t just detect failures but understands them. The AI agent you built combines the simplicity of EmbedChain’s RAG capabilities with the reliability of CircleCI’s automation, creating a solution that automatically processes complex error logs and delivers expert-level insights in minutes rather than hours. What once required senior developers to manually parse through voluminous log files, correlate errors, and identify patterns now happens automatically with every pipeline run, freeing your team to focus on solving problems rather than finding them
