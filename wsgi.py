"""
WSGI configuration for py4web CoolProp application on PythonAnywhere

This file should be referenced from PythonAnywhere's WSGI configuration.

For PythonAnywhere, your WSGI config should import from this file:
    from apps.coolpropgit.wsgi import application
"""

import os
import sys

# Get the directory containing this file (coolpropgit app directory)
COOLPROPGIT_FOLDER = os.path.dirname(os.path.abspath(__file__))

# Get the apps directory (parent directory)
APPS_FOLDER = os.path.dirname(COOLPROPGIT_FOLDER)

# Add apps folder to Python path if needed
if APPS_FOLDER not in sys.path:
    sys.path.insert(0, APPS_FOLDER)

# Change to the apps directory (py4web expects to run from apps folder)
os.chdir(APPS_FOLDER)

# Import py4web's WSGI handler
from py4web.core import wsgi

# Create the WSGI application
# This will serve all apps in the 'apps' folder
application = wsgi(apps_folder=APPS_FOLDER)
