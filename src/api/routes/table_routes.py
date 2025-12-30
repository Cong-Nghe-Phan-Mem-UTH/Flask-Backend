from flask import Blueprint, request
from services.table_service import (
    get_table_list_service,
    get_table_detail_service,
    create_table_service,
    update_table_service,
    delete_table_service
)
from api.middleware import require_logined, require_owner_or_employee, pause_api_check

table_bp = Blueprint('table', __name__, url_prefix='/tables')

@table_bp.route('/', methods=['GET'])
def get_table_list():
    return get_table_list_service()

@table_bp.route('/<int:number>', methods=['GET'])
def get_table_detail(number):
    return get_table_detail_service(number)

@table_bp.route('/', methods=['POST'])
@require_logined
@pause_api_check
@require_owner_or_employee
def create_table():
    return create_table_service(request.json)

@table_bp.route('/<int:number>', methods=['PUT'])
@require_logined
@pause_api_check
@require_owner_or_employee
def update_table(number):
    return update_table_service(number, request.json)

@table_bp.route('/<int:number>', methods=['DELETE'])
@require_logined
@pause_api_check
@require_owner_or_employee
def delete_table(number):
    return delete_table_service(number)

