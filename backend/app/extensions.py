"""
Flask extensions initialization.
Initialized without app (deferred init pattern).
"""

from flask_cors import CORS
from flask.logging import default_handler
import logging
import sys

cors = CORS()

# Structured logging setup
logger = logging.getLogger('aerospace_valve')


def init_logging(app):
    """Initialize structured logging."""
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    logger.setLevel(log_level)

    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s %(name)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.handlers.clear()
    logger.addHandler(console_handler)

    # File handler (if configured)
    log_file = app.config.get('LOG_FILE')
    if log_file:
        import os
        os.makedirs(os.path.dirname(log_file), exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    # Reduce werkzeug noise
    logging.getLogger('werkzeug').setLevel(logging.WARNING)


def init_extensions(app):
    """Initialize all Flask extensions with the app."""
    cors.init_app(app)
    init_logging(app)
    logger.info('Extensions initialized (config=%s)', app.config.get('ENV', 'unknown'))