from flask import jsonify, g
from infrastructure.databases import get_session
from infrastructure.models.guest_model import GuestModel
from infrastructure.models.table_model import TableModel
from infrastructure.models.dish_model import DishModel
from infrastructure.models.dish_model import DishSnapshotModel
from infrastructure.models.order_model import OrderModel
from utils.jwt_utils import sign_access_token, sign_refresh_token, verify_refresh_token
from domain.constants import Role, TableStatus, DishStatus, OrderStatus
from domain.exceptions import AuthError
from config import Config
from datetime import datetime
from utils.jwt_utils import parse_time_string
from utils.socket_utils import emit_to_manager

def guest_login_service(body):
    """Guest login"""
    session = get_session()
    try:
        table = session.query(TableModel).filter_by(
            number=body['tableNumber'],
            token=body['token']
        ).first()
        
        if not table:
            raise ValueError('Bàn không tồn tại hoặc mã token không đúng')
        
        if table.status == TableStatus.Hidden:
            raise ValueError('Bàn này đã bị ẩn, hãy chọn bàn khác để đăng nhập')
        
        if table.status == TableStatus.Reserved:
            raise ValueError('Bàn đã được đặt trước, hãy liên hệ nhân viên để được hỗ trợ')
        
        guest = GuestModel(
            name=body['name'],
            table_number=body['tableNumber']
        )
        session.add(guest)
        session.commit()
        session.refresh(guest)
        
        # Create tokens with guest expiry
        refresh_token_expires_in = parse_time_string(Config.GUEST_REFRESH_TOKEN_EXPIRES_IN)
        access_token_expires_in = parse_time_string(Config.GUEST_ACCESS_TOKEN_EXPIRES_IN)
        
        refresh_token = sign_refresh_token({
            'userId': guest.id,
            'role': Role.Guest
        }, expires_in=refresh_token_expires_in)
        
        access_token = sign_access_token({
            'userId': guest.id,
            'role': Role.Guest
        }, expires_in=access_token_expires_in)
        
        decoded_refresh_token = verify_refresh_token(refresh_token)
        refresh_token_expires_at = datetime.fromtimestamp(decoded_refresh_token['exp'])
        
        guest.refresh_token = refresh_token
        guest.refresh_token_expires_at = refresh_token_expires_at
        session.commit()
        
        return jsonify({
            'message': 'Đăng nhập thành công',
            'data': {
                'guest': {
                    'id': guest.id,
                    'name': guest.name,
                    'role': Role.Guest,
                    'tableNumber': guest.table_number,
                    'createdAt': guest.created_at.isoformat() if guest.created_at else None,
                    'updatedAt': guest.updated_at.isoformat() if guest.updated_at else None
                },
                'accessToken': access_token,
                'refreshToken': refresh_token
            }
        }), 200
    finally:
        session.close()

def guest_logout_service():
    """Guest logout"""
    from flask import abort
    session = get_session()
    try:
        guest = session.query(GuestModel).get(g.current_user_id)
        if not guest:
            abort(404)
        guest.refresh_token = None
        guest.refresh_token_expires_at = None
        session.commit()
        return jsonify({'message': 'Đăng xuất thành công'}), 200
    finally:
        session.close()

def guest_refresh_token_service(refresh_token):
    """Guest refresh token"""
    session = get_session()
    try:
        try:
            decoded = verify_refresh_token(refresh_token)
        except ValueError:
            raise AuthError('Refresh token không hợp lệ')
        
        guest = session.query(GuestModel).get(decoded['userId'])
        if not guest or guest.refresh_token != refresh_token:
            raise AuthError('Refresh token không hợp lệ')
        
        # Create new tokens
        refresh_token_expires_in = parse_time_string(Config.GUEST_REFRESH_TOKEN_EXPIRES_IN)
        access_token_expires_in = parse_time_string(Config.GUEST_ACCESS_TOKEN_EXPIRES_IN)
        
        new_refresh_token = sign_refresh_token({
            'userId': guest.id,
            'role': Role.Guest,
            'exp': decoded.get('exp')
        }, expires_in=refresh_token_expires_in)
        
        new_access_token = sign_access_token({
            'userId': guest.id,
            'role': Role.Guest
        }, expires_in=access_token_expires_in)
        
        guest.refresh_token = new_refresh_token
        guest.refresh_token_expires_at = datetime.fromtimestamp(decoded['exp'])
        session.commit()
        
        return jsonify({
            'message': 'Lấy token mới thành công',
            'data': {
                'accessToken': new_access_token,
                'refreshToken': new_refresh_token
            }
        }), 200
    finally:
        session.close()

def guest_create_orders_service(body):
    """Guest create orders"""
    from flask import abort
    session = get_session()
    try:
        guest = session.query(GuestModel).get(g.current_user_id)
        if not guest:
            abort(404)
        
        if guest.table_number is None:
            raise ValueError('Bàn của bạn đã bị xóa, vui lòng đăng xuất và đăng nhập lại một bàn mới')
        
        table = session.query(TableModel).get(guest.table_number)
        if not table:
            abort(404)
        
        if table.status == TableStatus.Hidden:
            raise ValueError(f'Bàn {table.number} đã bị ẩn, vui lòng đăng xuất và chọn bàn khác')
        
        if table.status == TableStatus.Reserved:
            raise ValueError(f'Bàn {table.number} đã được đặt trước, vui lòng đăng xuất và chọn bàn khác')
        
        orders = []
        for order_data in body:
            dish = session.query(DishModel).get(order_data['dishId'])
            if not dish:
                abort(404)
            
            if dish.status == DishStatus.Unavailable:
                raise ValueError(f'Món {dish.name} đã hết')
            
            if dish.status == DishStatus.Hidden:
                raise ValueError(f'Món {dish.name} không thể đặt')
            
            dish_snapshot = DishSnapshotModel(
                name=dish.name,
                price=dish.price,
                description=dish.description,
                image=dish.image,
                status=dish.status,
                dish_id=dish.id
            )
            session.add(dish_snapshot)
            session.flush()
            
            order = OrderModel(
                dish_snapshot_id=dish_snapshot.id,
                guest_id=guest.id,
                quantity=order_data['quantity'],
                table_number=guest.table_number,
                order_handler_id=None,
                status=OrderStatus.Pending
            )
            session.add(order)
            orders.append(order)
        
        session.commit()
        
        # Refresh orders to get relationships
        for order in orders:
            session.refresh(order)
        
        # Emit socket event
        orders_data = [order.to_dict() for order in orders]
        emit_to_manager('new-order', orders_data)
        
        return jsonify({
            'message': 'Đặt món thành công',
            'data': orders_data
        }), 200
    finally:
        session.close()

def guest_get_orders_service():
    """Guest get orders"""
    session = get_session()
    try:
        orders = session.query(OrderModel).filter_by(guest_id=g.current_user_id).all()
        return jsonify({
            'message': 'Lấy danh sách đơn hàng thành công',
            'data': [order.to_dict() for order in orders]
        }), 200
    finally:
        session.close()

