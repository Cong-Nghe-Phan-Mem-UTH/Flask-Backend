from flask import Blueprint, request, g
from services.order_service import (
    create_orders_service,
    get_orders_service,
    get_order_detail_service,
    update_order_service,
    pay_orders_service
)
from api.middleware import require_logined, require_owner_or_employee

order_bp = Blueprint('order', __name__, url_prefix='/orders')

@order_bp.route('/', methods=['POST'])
@require_logined
@require_owner_or_employee
def create_orders():
    return create_orders_service(request.json)

@order_bp.route('/', methods=['GET'])
@require_logined
@require_owner_or_employee
def get_orders():
    from_date = request.args.get('fromDate')
    to_date = request.args.get('toDate')
    return get_orders_service(from_date, to_date)

@order_bp.route('/<int:order_id>', methods=['GET'])
@require_logined
@require_owner_or_employee
def get_order_detail(order_id):
    return get_order_detail_service(order_id)

@order_bp.route('/<int:order_id>', methods=['PUT'])
@require_logined
@require_owner_or_employee
def update_order(order_id):
    body = request.json
    body['orderHandlerId'] = g.current_user_id
    return update_order_service(order_id, body)

@order_bp.route('/pay', methods=['POST'])
@require_logined
@require_owner_or_employee
def pay_orders():
    body = request.json
    body['orderHandlerId'] = g.current_user_id
    return pay_orders_service(body)

