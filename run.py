#!/usr/bin/env python3
"""
PDF to Excel Grouped Converter Application
Main entry point for the Flask application
"""
import os
from app import create_app

app = create_app()

if __name__ == '__main__':
    # Only enable debug mode in development (default), disable in production
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
