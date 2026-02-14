#!/bin/bash

# Run the Flask notes application
cd "$(dirname "$0")"

echo "Starting Flask Notes Application..."
echo "The application will be available at http://localhost:5000"
echo "Press Ctrl+C to stop the server"
echo ""

# Check if we can import the required modules
python3 -c "
import sys
try:
    from flask import Flask
    from flask_sqlalchemy import SQLAlchemy
    print('✓ All required modules are installed')
except ImportError as e:
    print(f'✗ Missing module: {e}')
    print('Please run: pip install -r requirements.txt')
    sys.exit(1)
"

# Run the application
python3 app.py