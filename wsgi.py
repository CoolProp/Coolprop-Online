"""
WSGI configuration for py4web CoolProp application

This file can be used directly or referenced from PythonAnywhere's WSGI configuration.

Usage on PythonAnywhere:
    1. Point WSGI file to this file's location, OR
    2. Import: from apps.coolpropgit.wsgi import application
"""

import os
import sys

# Get the directory containing this file (coolpropgit app directory)
COOLPROPGIT_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Get the apps directory (parent of coolpropgit)
APPS_FOLDER = os.path.dirname(COOLPROPGIT_FOLDER)

# Get the project root (parent of apps)
PROJECT_ROOT = os.path.dirname(APPS_FOLDER)

# Add both to path to ensure imports work
for path in [PROJECT_ROOT, APPS_FOLDER]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Change to the apps directory (py4web needs to run from here)
os.chdir(APPS_FOLDER)

# Import py4web's WSGI handler
from py4web.core import wsgi

# Create the WSGI application serving all apps
application = wsgi(apps_folder=APPS_FOLDER)
