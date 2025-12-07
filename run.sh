#!/bin/bash
# Simple script to run the Flask application

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies if needed
pip install -q -r requirements.txt

# Initialize database if it doesn't exist
if [ ! -f "app.db" ]; then
    echo "Initializing database..."
    python init_db.py
fi

# Run the application
echo "Starting Flask application..."
python app.py
