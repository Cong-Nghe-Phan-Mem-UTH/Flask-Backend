from flask import Blueprint, request
from services.dish_service import (
    get_dish_list_service,
    get_dish_list_with_pagination_service,
    get_dish_detail_service,
    create_dish_service,
    update_dish_service,
    delete_dish_service
)
from api.middleware import require_logined, require_owner_or_employee, pause_api_check

dish_bp = Blueprint('dish', __name__, url_prefix='/dishes')

@dish_bp.route('/', methods=['GET'])
def get_dish_list():
    return get_dish_list_service()

@dish_bp.route('/pagination', methods=['GET'])
def get_dish_list_with_pagination():
    page = int(request.args.get('page', 1))
    limit = int(request.args.get('limit', 10))
    return get_dish_list_with_pagination_service(page, limit)

@dish_bp.route('/<int:id>', methods=['GET'])
def get_dish_detail(id):
    return get_dish_detail_service(id)

@dish_bp.route('/', methods=['POST'])
@require_logined
@pause_api_check
@require_owner_or_employee
def create_dish():
    body = request.get_json()
    if not body:
        from domain.exceptions import EntityError
        raise EntityError([{'field': 'body', 'message': 'Dữ liệu không hợp lệ'}])
    return create_dish_service(body)

@dish_bp.route('/<int:id>', methods=['PUT'])
@require_logined
@pause_api_check
@require_owner_or_employee
def update_dish(id):
    return update_dish_service(id, request.json)

@dish_bp.route('/<int:id>', methods=['DELETE'])
@require_logined
@pause_api_check
@require_owner_or_employee
def delete_dish(id):
    return delete_dish_service(id)

