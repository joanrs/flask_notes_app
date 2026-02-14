#!/bin/bash

# Setup and run script for Flask Notes Application
# This script creates a virtual environment, installs dependencies, and runs the app

echo "🚀 Setting up Flask Notes Application..."
echo "========================================"

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the flask_notes_app directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "❌ Failed to create virtual environment"
        exit 1
    fi
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."

# Detect the operating system
if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    # Linux or macOS
    source venv/bin/activate
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
    # Windows
    source venv/Scripts/activate
else
    echo "⚠️  Unknown operating system, trying default activation"
    source venv/bin/activate || source venv/Scripts/activate
fi

if [ $? -ne 0 ]; then
    echo "❌ Failed to activate virtual environment"
    exit 1
fi

echo "✅ Virtual environment activated"

# Install dependencies
echo "📦 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    deactivate
    exit 1
fi

echo "✅ Dependencies installed"

# Create uploads directory if it doesn't exist
if [ ! -d "uploads" ]; then
    echo "📁 Creating uploads directory..."
    mkdir -p uploads
    echo "✅ Uploads directory created"
fi

# Run the application
echo "🚀 Starting Flask Notes Application..."
echo "========================================"
echo "The application will be available at: http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

python app.py

# When the application stops, deactivate the virtual environment
deactivate