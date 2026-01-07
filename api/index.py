"""
Vercel serverless entry point for Flask application
"""
import sys
import os

# Add src directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, '..', 'src')
sys.path.insert(0, src_dir)

# Set working directory to src for relative imports
os.chdir(src_dir)

# Import the Flask app
from create_app import create_app

# Create the app instance
# Note: Socket.IO may have limited support on Vercel serverless environment
# WebSocket connections might not work as expected
app, socketio = create_app()

# Export the app for Vercel
# Vercel will automatically detect and use the Flask app
# The app variable is the WSGI application that Vercel expects

