"""
Aerospace Valve R&D Platform - Application Entry Point
=====================================================
Uses the Flask Application Factory pattern for scalability and testability.
For development:  python app.py
For production:    gunicorn app:app --bind 0.0.0.0:$PORT
"""

import os
from app import create_app

# Create application instance
# FLASK_ENV can be 'development' (default), 'production', or 'test'
app = create_app(os.environ.get('FLASK_ENV'))

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug = app.config.get('DEBUG', False)
    app.run(host='0.0.0.0', port=port, debug=debug)
