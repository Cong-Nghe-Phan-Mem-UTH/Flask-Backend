from flask import Blueprint, send_from_directory, Response, current_app
from config import Config
import os

static_bp = Blueprint('static', __name__)

@static_bp.route('/<path:filename>')
def serve_static(filename):
    """Serve static files (images) with CORS headers"""
    # Log immediately to verify route is being called
    print(f"🔵 STATIC ROUTE CALLED: filename={filename}")
    current_app.logger.info(f"🔵 STATIC ROUTE CALLED: filename={filename}")
    try:
        # Security: prevent directory traversal
        filename = os.path.basename(filename)
        # Get upload folder from Config (class variable, no need to instantiate)
        upload_folder = Config.UPLOAD_FOLDER
        file_path = os.path.join(upload_folder, filename)
        
        # Log for debugging (use both print and logger)
        print(f"📁 Static request: filename={filename}")
        print(f"📁 Upload folder: {upload_folder}")
        print(f"📁 Full path: {file_path}")
        print(f"📁 Path exists: {os.path.exists(file_path)}")
        current_app.logger.info(f"📁 Static request: filename={filename}")
        current_app.logger.info(f"📁 Upload folder: {upload_folder}")
        current_app.logger.info(f"📁 Full path: {file_path}")
        current_app.logger.info(f"📁 Path exists: {os.path.exists(file_path)}")
        
        # Check if file exists
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            current_app.logger.error(f"❌ File not found: {file_path}")
            # List files in upload folder for debugging
            if os.path.exists(upload_folder):
                files = os.listdir(upload_folder)
                print(f"📁 Files in upload folder: {files[:10]}")  # Show first 10
                current_app.logger.info(f"📁 Files in upload folder: {files[:10]}")
            # Use abort to let Flask handle 404 properly
            from flask import abort
            abort(404)
        
        print(f"✅ Serving file: {file_path}")
        current_app.logger.info(f"✅ Serving file: {file_path}")
        response = send_from_directory(upload_folder, filename)
        
        # Add CORS headers for images
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'GET')
        response.headers.add('Cache-Control', 'public, max-age=31536000')  # Cache for 1 year
        
        return response
    except Exception as e:
        current_app.logger.error(f"❌ Error serving file: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        return {'message': f'Error serving file: {str(e)}'}, 500

