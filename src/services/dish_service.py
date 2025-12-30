from flask import jsonify, current_app
from infrastructure.databases import get_session
from infrastructure.models.dish_model import DishModel
from config import Config

def _format_image_url(image_path):
    """Format image URL to full URL if needed"""
    if not image_path:
        return None
    # If already a full URL (starts with http:// or https://), return as is
    if image_path.startswith('http://') or image_path.startswith('https://'):
        return image_path
    # If starts with /static/, return full URL
    if image_path.startswith('/static/'):
        return f"{Config().API_URL}{image_path}"
    # If just filename, prepend /static/
    if not image_path.startswith('/'):
        return f"{Config().API_URL}/static/{image_path}"
    return f"{Config().API_URL}{image_path}"

def get_dish_list_service():
    """Get all dishes (for public homepage)"""
    session = get_session()
    try:
        # Get all dishes, but prioritize Available ones
        # If no Available dishes, show all dishes
        available_dishes = session.query(DishModel).filter(
            DishModel.status == 'Available'
        ).order_by(DishModel.created_at.desc()).all()
        
        # If no available dishes, get all dishes
        if not available_dishes:
            dishes = session.query(DishModel).order_by(DishModel.created_at.desc()).all()
        else:
            dishes = available_dishes
        
        # Format dishes with full image URLs
        dishes_data = []
        for dish in dishes:
            dish_dict = dish.to_dict()
            dish_dict['image'] = _format_image_url(dish_dict['image'])
            dishes_data.append(dish_dict)
        
        response = jsonify({
            'data': dishes_data,
            'message': 'Lấy danh sách món ăn thành công!'
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    finally:
        session.close()

def get_dish_list_with_pagination_service(page, limit):
    """Get dishes with pagination"""
    session = get_session()
    try:
        offset = (page - 1) * limit
        # Only get dishes with status 'Available'
        dishes = session.query(DishModel).filter(
            DishModel.status == 'Available'
        ).order_by(DishModel.created_at.desc()).offset(offset).limit(limit).all()
        
        total_item = session.query(DishModel).filter(
            DishModel.status == 'Available'
        ).count()
        total_page = (total_item + limit - 1) // limit
        
        # Format dishes with full image URLs
        dishes_data = []
        for dish in dishes:
            dish_dict = dish.to_dict()
            dish_dict['image'] = _format_image_url(dish_dict['image'])
            dishes_data.append(dish_dict)
        
        response = jsonify({
            'data': {
                'items': dishes_data,
                'totalItem': total_item,
                'totalPage': total_page,
                'page': page,
                'limit': limit
            },
            'message': 'Lấy danh sách món ăn thành công!'
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    finally:
        session.close()

def get_dish_detail_service(dish_id):
    """Get dish detail"""
    session = get_session()
    try:
        dish = session.query(DishModel).get_or_404(dish_id)
        dish_dict = dish.to_dict()
        dish_dict['image'] = _format_image_url(dish_dict['image'])
        response = jsonify({
            'data': dish_dict,
            'message': 'Lấy thông tin món ăn thành công!'
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    finally:
        session.close()

def create_dish_service(body):
    """Create dish"""
    session = get_session()
    try:
        dish = DishModel(
            name=body['name'],
            price=body['price'],
            description=body['description'],
            image=body['image'],
            status=body.get('status', 'Available')
        )
        session.add(dish)
        session.commit()
        session.refresh(dish)
        dish_dict = dish.to_dict()
        dish_dict['image'] = _format_image_url(dish_dict['image'])
        return jsonify({
            'data': dish_dict,
            'message': 'Tạo món ăn thành công!'
        }), 200
    finally:
        session.close()

def update_dish_service(dish_id, body):
    """Update dish"""
    session = get_session()
    try:
        dish = session.query(DishModel).get_or_404(dish_id)
        dish.name = body.get('name', dish.name)
        dish.price = body.get('price', dish.price)
        dish.description = body.get('description', dish.description)
        dish.image = body.get('image', dish.image)
        dish.status = body.get('status', dish.status)
        session.commit()
        session.refresh(dish)
        dish_dict = dish.to_dict()
        dish_dict['image'] = _format_image_url(dish_dict['image'])
        return jsonify({
            'data': dish_dict,
            'message': 'Cập nhật món ăn thành công!'
        }), 200
    finally:
        session.close()

def delete_dish_service(dish_id):
    """Delete dish"""
    session = get_session()
    try:
        dish = session.query(DishModel).get_or_404(dish_id)
        session.delete(dish)
        session.commit()
        return jsonify({
            'data': dish.to_dict(),
            'message': 'Xóa món ăn thành công!'
        }), 200
    finally:
        session.close()

