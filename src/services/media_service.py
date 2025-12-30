from flask import jsonify, request
from werkzeug.utils import secure_filename
from utils.helpers import random_id
from config import Config
import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def upload_image_service():
    """Upload image"""
    if 'file' not in request.files:
        raise ValueError('Không tìm thấy file')
    
    file = request.files['file']
    if file.filename == '':
        raise ValueError('Không tìm thấy file')
    
    if not allowed_file(file.filename):
        raise ValueError('File không hợp lệ. Chỉ chấp nhận: png, jpg, jpeg, gif, webp')
    
    # Check file size (10MB)
    file.seek(0, os.SEEK_END)
    file_length = file.tell()
    file.seek(0)
    if file_length > 10 * 1024 * 1024:
        raise ValueError('Giới hạn file là 10MB')
    
    unique_id = random_id()
    ext = os.path.splitext(file.filename)[1]
    filename = unique_id + ext
    filepath = os.path.join(Config.UPLOAD_FOLDER, filename)
    
    file.save(filepath)
    url = f"{Config.API_URL}/static/{filename}"
    
    return jsonify({
        'message': 'Upload ảnh thành công',
        'data': url
    }), 200

