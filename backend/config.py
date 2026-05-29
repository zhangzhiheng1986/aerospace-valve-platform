"""
Configuration management for Aerospace Valve R&D Platform.
Supports development, testing, and production environments.
"""

import os


class Config:
    """Base configuration."""

    # Flask
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

    # JWT
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    JWT_EXPIRES_HOURS = 24

    # CORS
    CORS_ORIGINS = ['*']

    # Logging
    LOG_LEVEL = 'INFO'
    LOG_FILE = None

    # Upload
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB

    # Serveo / Public URL (set via env)
    PUBLIC_URL = os.environ.get('PUBLIC_URL', 'http://localhost:5000')


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    LOG_LEVEL = 'DEBUG'
    LOG_FILE = 'logs/dev.log'


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    LOG_LEVEL = 'WARNING'
    # In production, PUBLIC_URL should be set via environment
    CORS_ORIGINS = os.environ.get('CORS_ORIGINS', '*').split(',')


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    DEBUG = True


config_by_name = {
    'dev': DevelopmentConfig,
    'development': DevelopmentConfig,
    'prod': ProductionConfig,
    'production': ProductionConfig,
    'test': TestingConfig,
    'testing': TestingConfig,
}

# Default config
default_config = 'development'
