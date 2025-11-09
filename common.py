"""
Common initialization for CoolProp py4web application
This replaces web2py's models/db.py and models/menu.py
"""
import os
from py4web import Session, Flash
from py4web.utils.auth import Auth
from pydal.validators import *
from .models import db

# Create databases folder if it doesn't exist
os.makedirs(os.path.join(os.path.dirname(__file__), "databases"), exist_ok=True)

# Session configuration
session = Session(secret="change-this-to-a-secret-key")

# Flash messages for passing messages between page loads
flash = Flash()

# Auth configuration
auth = Auth(session, db, define_tables=True)

# Configure auth settings
auth.param.registration_requires_confirmation = False
auth.param.registration_requires_approval = False
auth.param.login_after_registration = True

# This will be used by controllers
T = lambda s: s  # Simple translation function, can be enhanced later
