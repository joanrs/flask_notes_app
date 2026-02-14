#!/bin/bash

# Activate virtual environment and run tests

echo "🔧 Activating virtual environment and running tests..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app.py" ]; then
    echo "❌ Error: Please run this script from the flask_notes_app directory"
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup_and_run.sh first."
    exit 1
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."

if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
    source venv/bin/activate
elif [[ "$OSTYPE" == "cygwin" || "$OSTYPE" == "msys" || "$OSTYPE" == "win32" ]]; then
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

# Run the test suite
echo "🧪 Running test suite..."
python test_app.py

test_result=$?

if [ $test_result -eq 0 ]; then
    echo "✅ All tests passed!"
else
    echo "❌ Some tests failed"
fi

# Deactivate virtual environment
deactivate

exit $test_result