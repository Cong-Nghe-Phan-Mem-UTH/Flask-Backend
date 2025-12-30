from flask import jsonify, g
from infrastructure.databases import get_session
from infrastructure.models.order_model import OrderModel
from infrastructure.models.guest_model import GuestModel
from infrastructure.models.table_model import TableModel
from infrastructure.models.dish_model import DishModel, DishSnapshotModel
from infrastructure.models.socket_model import SocketModel
from domain.constants import DishStatus, OrderStatus, TableStatus
from utils.socket_utils import emit_to_manager_and_socket, emit_to_manager

def create_orders_service(body):
    """Create orders"""
    session = get_session()
    try:
        guest_id = body['guestId']
        orders_data = body['orders']
        
        guest = session.query(GuestModel).get_or_404(guest_id)
        if guest.table_number is None:
            raise ValueError('Bàn gắn liền với khách hàng này đã bị xóa, vui lòng chọn khách hàng khác!')
        
        table = session.query(TableModel).get_or_404(guest.table_number)
        if table.status == TableStatus.Hidden:
            raise ValueError(f'Bàn {table.number} gắn liền với khách hàng đã bị ẩn, vui lòng chọn khách hàng khác!')
        
        # Get socket record before creating orders
        socket_record = session.query(SocketModel).filter_by(guest_id=guest_id).first()
        
        orders = []
        for order_data in orders_data:
            dish = session.query(DishModel).get_or_404(order_data['dishId'])
            
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
                guest_id=guest_id,
                quantity=order_data['quantity'],
                table_number=guest.table_number,
                order_handler_id=g.current_user_id,
                status=OrderStatus.Pending
            )
            session.add(order)
            orders.append(order)
        
        session.commit()
        
        # Refresh orders
        for order in orders:
            session.refresh(order)
        
        # Emit socket event
        orders_data = [order.to_dict() for order in orders]
        socket_id = socket_record.socket_id if socket_record else None
        if socket_id:
            emit_to_manager_and_socket(socket_id, 'new-order', orders_data)
        else:
            emit_to_manager('new-order', orders_data)
        
        return jsonify({
            'message': f'Tạo thành công {len(orders)} đơn hàng cho khách hàng',
            'data': orders_data
        }), 200
    finally:
        session.close()

def get_orders_service(from_date=None, to_date=None):
    """Get orders"""
    session = get_session()
    try:
        query = session.query(OrderModel)
        if from_date:
            query = query.filter(OrderModel.created_at >= from_date)
        if to_date:
            query = query.filter(OrderModel.created_at <= to_date)
        
        orders = query.order_by(OrderModel.created_at.desc()).all()
        return jsonify({
            'message': 'Lấy danh sách đơn hàng thành công',
            'data': [order.to_dict() for order in orders]
        }), 200
    finally:
        session.close()

def get_order_detail_service(order_id):
    """Get order detail"""
    session = get_session()
    try:
        order = session.query(OrderModel).get_or_404(order_id)
        return jsonify({
            'message': 'Lấy đơn hàng thành công',
            'data': order.to_dict()
        }), 200
    finally:
        session.close()

def update_order_service(order_id, body):
    """Update order"""
    session = get_session()
    try:
        order = session.query(OrderModel).get_or_404(order_id)
        status = body.get('status')
        dish_id = body.get('dishId')
        quantity = body.get('quantity')
        
        dish_snapshot_id = order.dish_snapshot_id
        if dish_id and order.dish_snapshot.dish_id != dish_id:
            dish = session.query(DishModel).get_or_404(dish_id)
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
            dish_snapshot_id = dish_snapshot.id
        
        order.status = status or order.status
        order.dish_snapshot_id = dish_snapshot_id
        order.quantity = quantity or order.quantity
        order.order_handler_id = g.current_user_id
        
        socket_record = session.query(SocketModel).filter_by(guest_id=order.guest_id).first()
        session.commit()
        session.refresh(order)
        
        # Emit socket event
        order_data = order.to_dict()
        socket_id = socket_record.socket_id if socket_record else None
        if socket_id:
            emit_to_manager_and_socket(socket_id, 'update-order', order_data)
        else:
            emit_to_manager('update-order', order_data)
        
        return jsonify({
            'message': 'Cập nhật đơn hàng thành công',
            'data': order_data
        }), 200
    finally:
        session.close()

def pay_orders_service(body):
    """Pay orders"""
    session = get_session()
    try:
        guest_id = body['guestId']
        orders = session.query(OrderModel).filter(
            OrderModel.guest_id == guest_id,
            OrderModel.status.in_([OrderStatus.Pending, OrderStatus.Processing, OrderStatus.Delivered])
        ).all()
        
        if len(orders) == 0:
            raise ValueError('Không có hóa đơn nào cần thanh toán')
        
        order_ids = [order.id for order in orders]
        session.query(OrderModel).filter(OrderModel.id.in_(order_ids)).update({
            'status': OrderStatus.Paid,
            'order_handler_id': g.current_user_id
        }, synchronize_session=False)
        
        socket_record = session.query(SocketModel).filter_by(guest_id=guest_id).first()
        session.commit()
        
        # Refresh orders
        paid_orders = session.query(OrderModel).filter(OrderModel.id.in_(order_ids)).all()
        orders_data = [order.to_dict() for order in paid_orders]
        
        # Emit socket event
        socket_id = socket_record.socket_id if socket_record else None
        if socket_id:
            emit_to_manager_and_socket(socket_id, 'payment', orders_data)
        else:
            emit_to_manager('payment', orders_data)
        
        return jsonify({
            'message': f'Thanh toán thành công {len(paid_orders)} đơn',
            'data': orders_data
        }), 200
    finally:
        session.close()

