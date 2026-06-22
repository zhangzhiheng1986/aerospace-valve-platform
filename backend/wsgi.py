"""WSGI entry point for gunicorn production deployment.

Usage:
    gunicorn --bind 0.0.0.0:$PORT --workers 2 --threads 4 wsgi:app
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from config import default_config
config_name = os.environ.get('FLASK_ENV', default_config)

from app import create_app
app = create_app(config_name)
