from flask import Blueprint, send_from_directory, Response
from config import Config
import os

static_bp = Blueprint('static', __name__, url_prefix='/static')

@static_bp.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (images) with CORS headers"""
    try:
        # Security: prevent directory traversal
        filename = os.path.basename(filename)
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            return {'message': 'File not found'}, 404
        
        response = send_from_directory(Config.UPLOAD_FOLDER, filename)
        
        # Add CORS headers for images
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        response.headers.add('Cache-Control', 'public, max-age=31536000')  # Cache for 1 year
        
        return response
    except Exception as e:
        return {'message': f'Error serving file: {str(e)}'}, 500

