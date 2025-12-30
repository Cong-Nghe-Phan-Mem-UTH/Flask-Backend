from flask import jsonify
from infrastructure.databases import get_session
from infrastructure.models.order_model import OrderModel
from infrastructure.models.guest_model import GuestModel
from infrastructure.models.dish_model import DishModel
from domain.constants import OrderStatus
from config import Config
from datetime import timedelta
from dateutil import parser
from dateutil.tz import gettz

def dashboard_indicator_service(from_date, to_date):
    """Get dashboard indicators"""
    session = get_session()
    try:
        # Parse dates
        if isinstance(from_date, str):
            from_date = parser.parse(from_date)
        if isinstance(to_date, str):
            to_date = parser.parse(to_date)
        
        # Get orders
        orders = session.query(OrderModel).filter(
            OrderModel.created_at >= from_date,
            OrderModel.created_at <= to_date
        ).order_by(OrderModel.created_at.desc()).all()
        
        # Get guests with paid orders
        guest_ids = set()
        for order in orders:
            if order.status == OrderStatus.Paid and order.guest_id:
                guest_ids.add(order.guest_id)
        
        guests = session.query(GuestModel).filter(GuestModel.id.in_(list(guest_ids))).all()
        
        # Get all dishes
        dishes = session.query(DishModel).all()
        
        # Calculate revenue
        revenue = 0
        guest_count = len(guests)
        order_count = len(orders)
        
        # Dish indicator
        dish_indicator_obj = {}
        for dish in dishes:
            dish_indicator_obj[dish.id] = {
                'id': dish.id,
                'name': dish.name,
                'price': dish.price,
                'description': dish.description,
                'image': dish.image,
                'status': dish.status,
                'createdAt': dish.created_at.isoformat() if dish.created_at else None,
                'updatedAt': dish.updated_at.isoformat() if dish.updated_at else None,
                'successOrders': 0
            }
        
        # Revenue by date
        revenue_by_date_obj = {}
        current_date = from_date
        tz = gettz(Config.SERVER_TIMEZONE)
        
        while current_date <= to_date:
            date_str = current_date.strftime('%d/%m/%Y')
            revenue_by_date_obj[date_str] = 0
            current_date += timedelta(days=1)
        
        # Table number obj
        table_number_obj = {}
        
        # Process orders
        from infrastructure.models.dish_model import DishSnapshotModel
        for order in orders:
            if order.status == OrderStatus.Paid:
                # Get dish snapshot price
                dish_snapshot = session.query(DishSnapshotModel).get(order.dish_snapshot_id)
                if dish_snapshot:
                    order_revenue = dish_snapshot.price * order.quantity
                    revenue += order_revenue
                    
                    if dish_snapshot.dish_id and dish_snapshot.dish_id in dish_indicator_obj:
                        dish_indicator_obj[dish_snapshot.dish_id]['successOrders'] += 1
                    
                    # Revenue by date
                    date_str = order.created_at.strftime('%d/%m/%Y')
                    if date_str in revenue_by_date_obj:
                        revenue_by_date_obj[date_str] += order_revenue
            
            if order.status in [OrderStatus.Processing, OrderStatus.Pending, OrderStatus.Delivered]:
                if order.table_number:
                    table_number_obj[order.table_number] = True
        
        serving_table_count = len(table_number_obj)
        
        # Revenue by date
        revenue_by_date = [{'date': date, 'revenue': revenue} for date, revenue in revenue_by_date_obj.items()]
        dish_indicator = list(dish_indicator_obj.values())
        
        return jsonify({
            'message': 'Lấy các chỉ số thành công',
            'data': {
                'revenue': revenue,
                'guestCount': guest_count,
                'orderCount': order_count,
                'servingTableCount': serving_table_count,
                'dishIndicator': dish_indicator,
                'revenueByDate': revenue_by_date
            }
        }), 200
    finally:
        session.close()

