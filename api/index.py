import os
import sys

# Ensure project root is in Python module search path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import create_app

# Create Flask application instance for Vercel Serverless Function
app = create_app(os.environ.get('FLASK_ENV', 'production'))

# Expose app for Vercel Python WSGI runtime
# (Vercel automatically discovers 'app' in api/index.py)
