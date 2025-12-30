from flask import Blueprint, request
from services.indicator_service import dashboard_indicator_service
from api.middleware import require_logined, require_owner_or_employee

indicator_bp = Blueprint('indicator', __name__, url_prefix='/indicators')

@indicator_bp.route('/dashboard', methods=['GET'])
@require_logined
@require_owner_or_employee
def dashboard_indicator():
    from_date = request.args.get('fromDate')
    to_date = request.args.get('toDate')
    
    if not from_date or not to_date:
        from flask import jsonify
        return jsonify({'message': 'Thiếu fromDate hoặc toDate'}), 400
    
    return dashboard_indicator_service(from_date, to_date)

