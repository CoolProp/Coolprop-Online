"""
py4web application settings
"""
import os

# Application info
APP_NAME = "coolpropgit"
APP_FOLDER = os.path.dirname(__file__)

# Database settings
DB_URI = "sqlite://storage.db"
DB_POOL_SIZE = 1
DB_MIGRATE = True
DB_FAKE_MIGRATE = False

# Session settings
SESSION_TYPE = "database"
SESSION_SECRET_KEY = None  # Will be auto-generated if None

# Security settings
ALLOWED_HOSTS = ["*"]  # Update for production

# Email settings (for auth)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USERNAME = "you@gmail.com"
SMTP_PASSWORD = "password"
SMTP_TLS = True
SMTP_SSL = False

# Logging
import logging
LOGGERS = [logging.WARNING]
