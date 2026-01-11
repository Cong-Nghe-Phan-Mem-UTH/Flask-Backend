from flask import jsonify, g, current_app
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
        
        from flask import abort
        guest = session.query(GuestModel).get(guest_id)
        if not guest:
            abort(404)
        if guest.table_number is None:
            raise ValueError('Bàn gắn liền với khách hàng này đã bị xóa, vui lòng chọn khách hàng khác!')
        
        table = session.query(TableModel).get(guest.table_number)
        if not table:
            abort(404)
        if table.status == TableStatus.Hidden:
            raise ValueError(f'Bàn {table.number} gắn liền với khách hàng đã bị ẩn, vui lòng chọn khách hàng khác!')
        
        # Get socket record before creating orders
        socket_record = session.query(SocketModel).filter_by(guest_id=guest_id).first()
        
        orders = []
        for order_data in orders_data:
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
    from infrastructure.models.dish_model import DishSnapshotModel
    from infrastructure.models.guest_model import GuestModel
    from config import Config
    
    def _format_image_url(image_path):
        """Format image URL to full URL if needed"""
        if not image_path:
            return None
        
        # If already a full URL, normalize it first (extract filename)
        if image_path.startswith('http://') or image_path.startswith('https://'):
            # Extract filename from URL (normalize production URLs to filename)
            if '/static/' in image_path:
                normalized_path = image_path.split('/static/')[-1]
            else:
                # Try to extract last part of URL
                normalized_path = image_path.split('/')[-1]
        else:
            # Normalize path (remove leading slash and static/ prefix if exists)
            normalized_path = str(image_path).lstrip('/')
            if normalized_path.startswith('static/'):
                normalized_path = normalized_path[7:]
        
        # If path is empty after normalization, return None
        if not normalized_path:
            return None
        
        # Get API URL from config instance
        config = Config()
        api_url = config.API_URL
        result_url = f"{api_url}/static/{normalized_path}"
        return result_url
    
    session = get_session()
    try:
        query = session.query(OrderModel)
        if from_date:
            query = query.filter(OrderModel.created_at >= from_date)
        if to_date:
            query = query.filter(OrderModel.created_at <= to_date)
        
        orders = query.order_by(OrderModel.created_at.desc()).all()
        
        # Build response with dishSnapshot and guest included
        orders_data = []
        for order in orders:
            order_dict = order.to_dict()
            
            # Query dish_snapshot separately
            dish_snapshot = session.query(DishSnapshotModel).get(order.dish_snapshot_id)
            if dish_snapshot:
                dish_snapshot_dict = dish_snapshot.to_dict()
                # Format image URL to full URL
                dish_snapshot_dict['image'] = _format_image_url(dish_snapshot_dict.get('image'))
                order_dict['dishSnapshot'] = dish_snapshot_dict
            else:
                # If dish_snapshot not found, set to null to prevent frontend errors
                current_app.logger.warning(f"⚠️  DishSnapshot {order.dish_snapshot_id} not found for order {order.id}")
                order_dict['dishSnapshot'] = None
            
            # Query guest separately if exists
            if order.guest_id:
                guest = session.query(GuestModel).get(order.guest_id)
                if guest:
                    order_dict['guest'] = guest.to_dict()
                else:
                    order_dict['guest'] = None
            else:
                order_dict['guest'] = None
            
            orders_data.append(order_dict)
        
        return jsonify({
            'message': 'Lấy danh sách đơn hàng thành công',
            'data': orders_data
        }), 200
    finally:
        session.close()

def get_order_detail_service(order_id):
    """Get order detail"""
    from flask import abort
    session = get_session()
    try:
        order = session.query(OrderModel).get(order_id)
        if not order:
            abort(404)
        return jsonify({
            'message': 'Lấy đơn hàng thành công',
            'data': order.to_dict()
        }), 200
    finally:
        session.close()

def update_order_service(order_id, body):
    """Update order"""
    from flask import abort
    session = get_session()
    try:
        order = session.query(OrderModel).get(order_id)
        if not order:
            abort(404)
        status = body.get('status')
        dish_id = body.get('dishId')
        quantity = body.get('quantity')
        
        dish_snapshot_id = order.dish_snapshot_id
        if dish_id and order.dish_snapshot.dish_id != dish_id:
            dish = session.query(DishModel).get(dish_id)
            if not dish:
                abort(404)
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

