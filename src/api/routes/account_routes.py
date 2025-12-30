from flask import Blueprint, request, jsonify, g
from services.account_service import (
    get_account_list_service,
    create_employee_account_service,
    get_employee_account_service,
    update_employee_account_service,
    delete_employee_account_service,
    get_me_service,
    update_me_service,
    change_password_service,
    change_password_v2_service,
    get_guest_list_service,
    create_guest_service
)
from api.middleware import require_logined, require_owner, require_owner_or_employee, pause_api_check

account_bp = Blueprint('account', __name__, url_prefix='/accounts')

@account_bp.route('/', methods=['GET'])
@require_owner
def get_account_list():
    return get_account_list_service()

@account_bp.route('/', methods=['POST'])
@require_owner
@pause_api_check
def create_employee_account():
    return create_employee_account_service(request.json)

@account_bp.route('/detail/<int:id>', methods=['GET'])
@require_owner
def get_employee_account(id):
    return get_employee_account_service(id)

@account_bp.route('/detail/<int:id>', methods=['PUT'])
@require_owner
@pause_api_check
def update_employee_account(id):
    return update_employee_account_service(id, request.json)

@account_bp.route('/detail/<int:id>', methods=['DELETE'])
@require_owner
@pause_api_check
def delete_employee_account(id):
    return delete_employee_account_service(id)

@account_bp.route('/me', methods=['GET'])
@require_logined
def get_me():
    return get_me_service()

@account_bp.route('/me', methods=['PUT'])
@require_logined
@pause_api_check
def update_me():
    return update_me_service(request.json)

@account_bp.route('/change-password', methods=['PUT'])
@require_logined
@pause_api_check
def change_password():
    return change_password_service(request.json)

@account_bp.route('/change-password-v2', methods=['PUT'])
@require_logined
@pause_api_check
def change_password_v2():
    return change_password_v2_service(request.json)

@account_bp.route('/guests', methods=['POST'])
@require_owner_or_employee
def create_guest():
    return create_guest_service(request.json)

@account_bp.route('/guests', methods=['GET'])
@require_owner_or_employee
def get_guest_list():
    from_date = request.args.get('fromDate')
    to_date = request.args.get('toDate')
    return get_guest_list_service(from_date, to_date)

