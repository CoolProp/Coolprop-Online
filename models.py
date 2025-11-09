"""
Database models for CoolProp application (migrated from web2py to py4web)
"""
from py4web import DAL
from pydal.validators import *
import os

# Database connection
db = DAL(
    "sqlite://storage.db",
    folder=os.path.join(os.path.dirname(__file__), "databases"),
    pool_size=1,
    check_reserved=['all']
)

# Auth tables will be defined in common.py by py4web's auth system
# The original web2py app used basic auth, which we'll configure in common.py
