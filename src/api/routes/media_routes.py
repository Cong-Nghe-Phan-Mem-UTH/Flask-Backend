from flask import Blueprint, request, current_app, jsonify
from services.media_service import upload_image_service
from api.middleware import require_logined, require_owner_or_employee, pause_api_check

media_bp = Blueprint('media', __name__, url_prefix='/media')

@media_bp.route('/test', methods=['GET', 'POST'])
def test_upload():
    """Test endpoint to check if request is received"""
    return jsonify({
        'message': 'Media route is working',
        'method': request.method,
        'content_type': request.content_type,
        'has_files': bool(request.files),
        'file_keys': list(request.files.keys()) if request.files else [],
        'form_keys': list(request.form.keys()) if request.form else []
    }), 200

@media_bp.route('/upload', methods=['POST', 'OPTIONS'])
@require_logined
@pause_api_check
@require_owner_or_employee
def upload_image():
    # Log request details for debugging
    current_app.logger.info(f"🔍 Media upload route hit - Method: {request.method}")
    current_app.logger.info(f"🔍 Content-Type: {request.content_type}")
    current_app.logger.info(f"🔍 Has files: {bool(request.files)}")
    if request.files:
        current_app.logger.info(f"🔍 File keys: {list(request.files.keys())}")
    return upload_image_service()

