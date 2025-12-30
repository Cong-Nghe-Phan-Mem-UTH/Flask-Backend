from flask import Blueprint, request, g
from services.guest_service import (
    guest_login_service,
    guest_logout_service,
    guest_refresh_token_service,
    guest_create_orders_service,
    guest_get_orders_service
)
from api.middleware import require_logined, require_guest

guest_bp = Blueprint('guest', __name__, url_prefix='/guest')

@guest_bp.route('/auth/login', methods=['POST'])
def guest_login():
    return guest_login_service(request.json)

@guest_bp.route('/auth/logout', methods=['POST'])
@require_logined
def guest_logout():
    return guest_logout_service()

@guest_bp.route('/auth/refresh-token', methods=['POST'])
def guest_refresh_token():
    return guest_refresh_token_service(request.json.get('refreshToken'))

@guest_bp.route('/orders', methods=['POST'])
@require_logined
@require_guest
def guest_create_orders():
    return guest_create_orders_service(request.json)

@guest_bp.route('/orders', methods=['GET'])
@require_logined
@require_guest
def guest_get_orders():
    return guest_get_orders_service()

