#!/bin/bash

# Flask Notes App with Vue 3 - Run Script
# ========================================

echo "🚀 Starting Flask Notes App with Vue 3"
echo "========================================"
echo ""

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected: flask_notes_app directory"
    exit 1
fi

# Check Python version
PYTHON_VERSION=$(python3.12 --version 2>&1)
if [[ $PYTHON_VERSION != "Python 3.12"* ]]; then
    echo "⚠️  Warning: Python 3.12 not found, trying python3..."
    PYTHON_CMD="python3"
else
    PYTHON_CMD="python3.12"
fi

# Create uploads directory if it doesn't exist
if [ ! -d "uploads" ]; then
    echo "📁 Creating uploads directory..."
    mkdir -p uploads
fi

# Initialize database
echo "🗃️  Initializing database..."
$PYTHON_CMD -c "
from app import app, db
from sqlalchemy import text
with app.app_context():
    db.create_all()
    # Create default category if none exists
    from models import Category
    if not Category.query.first():
        default_category = Category(name='General', color='#ffffff')
        db.session.add(default_category)
        db.session.commit()
        print('✅ Database initialized with default category')
    else:
        print('✅ Database already initialized')
"

# Check if tests should be run
if [ "$1" = "--test" ]; then
    echo "🧪 Running tests..."
    $PYTHON_CMD test_vue_integration.py
    if [ $? -ne 0 ]; then
        echo "❌ Vue integration tests failed"
        exit 1
    fi
    
    $PYTHON_CMD test_flask_vue_app.py
    if [ $? -ne 0 ]; then
        echo "❌ Application tests failed"
        exit 1
    fi
    
    echo "✅ All tests passed!"
fi

echo ""
echo "🌐 Starting Flask development server..."
echo "========================================"
echo ""
echo "📋 Application Info:"
echo "   • Flask Backend: Ready"
echo "   • Vue 3 Frontend: Integrated"
echo "   • Database: SQLite (notes.db)"
echo "   • Uploads: ./uploads/ directory"
echo ""
echo "🔗 Access the application at:"
echo "   http://localhost:5000"
echo ""
echo "📝 Features:"
echo "   • Notes Table View (Vue 3 with real-time filtering)"
echo "   • Notes Keep View (Vue 3 with card layout)"
echo "   • Categories management"
echo "   • User authentication"
echo "   • File attachments"
echo "   • Likes system"
echo ""
echo "⌨️  Press Ctrl+C to stop the server"
echo ""

# Start the Flask application
$PYTHON_CMD app.py
