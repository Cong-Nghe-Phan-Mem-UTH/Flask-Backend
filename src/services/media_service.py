from flask import jsonify, request, current_app
from werkzeug.utils import secure_filename
from utils.helpers import random_id, create_folder
from config import Config
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image_service():
    """Upload image"""
    try:
        current_app.logger.info(f"📤 Upload request - Content-Type: {request.content_type}")
        current_app.logger.info(f"📤 Upload request - Files: {list(request.files.keys())}")

        if 'file' not in request.files:
            from domain.exceptions import EntityError
            raise EntityError([{'field': 'file', 'message': 'Không tìm thấy file'}])
        
        file = request.files['file']
        if file.filename == '':
            from domain.exceptions import EntityError
            raise EntityError([{'field': 'file', 'message': 'Không tìm thấy file'}])
        
        if not allowed_file(file.filename):
            from domain.exceptions import EntityError
            raise EntityError([{'field': 'file', 'message': 'File không hợp lệ. Chỉ chấp nhận: png, jpg, jpeg, gif, webp'}])
        
        # Check file size (10MB)
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        if file_length > 10 * 1024 * 1024:
            from domain.exceptions import EntityError
            raise EntityError([{'field': 'file', 'message': 'Giới hạn file là 10MB'}])
        
        # Ensure upload folder exists
        create_folder(Config.UPLOAD_FOLDER)
        current_app.logger.info(f"📤 Upload folder: {Config.UPLOAD_FOLDER}")
        
        unique_id = random_id()
        ext = os.path.splitext(file.filename)[1].lower()
        filename = unique_id + ext
        filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
        
        current_app.logger.info(f"📤 Upload file name: {file.filename}")
        current_app.logger.info(f"📤 Upload file size: {file_length} bytes")
        current_app.logger.info(f"📤 Saving file to: {filepath}")
        
        # Save file
        file.save(filepath)
        
        # Verify file was saved
        if not os.path.exists(filepath):
            from domain.exceptions import EntityError
            raise EntityError([{'field': 'file', 'message': 'Lỗi khi lưu file'}])
        
        file_size = os.path.getsize(filepath)
        current_app.logger.info(f"✅ File saved successfully. Size: {file_size} bytes")

        config = Config() # Instantiate Config
        api_url = config.API_URL # Access property correctly
        url = f"{api_url}/static/{filename}"
        current_app.logger.info(f"✅ Upload URL: {url}")
        
        response = jsonify({
            'message': 'Upload ảnh thành công',
            'data': url
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except Exception as e:
        current_app.logger.error(f"❌ Error in upload_image_service: {str(e)}")
        # Re-raise EntityError as is
        if isinstance(e, Exception) and hasattr(e, 'errors'):
            raise
        # Convert other errors to EntityError
        from domain.exceptions import EntityError
        raise EntityError([{'field': 'file', 'message': f'Lỗi upload: {str(e)}'}])

