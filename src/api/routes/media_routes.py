from flask import Blueprint
from services.media_service import upload_image_service
from api.middleware import require_logined, require_owner_or_employee, pause_api_check

media_bp = Blueprint('media', __name__, url_prefix='/media')

@media_bp.route('/upload', methods=['POST'])
@require_logined
@pause_api_check
@require_owner_or_employee
def upload_image():
    return upload_image_service()

