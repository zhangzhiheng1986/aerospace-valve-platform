"""Flask application entry point - creates app from factory and runs dev server."""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

# Note: this file intentionally avoids using the 'app' package name
# to prevent namespace collisions on Linux (where case-insensitive
# package lookups can confuse 'app' with system modules).

if __name__ == '__main__':
    from config import default_config
    config_name = os.environ.get('FLASK_ENV', default_config)
    print(f'Starting Flask ({config_name}) on port 5000...')
    from app import create_app
    app = create_app(config_name)
    app.run(debug=True, host='0.0.0.0', port=5000)
