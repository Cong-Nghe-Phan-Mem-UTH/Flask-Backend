from flask import jsonify, current_app
from infrastructure.databases import get_session
from infrastructure.models.dish_model import DishModel
from config import Config
from utils.socket_utils import emit_to_manager

def _normalize_image_path(image_path):
    """Normalize image path to store in database (extract filename from URL if needed)"""
    if not image_path:
        return ''
    
    # If it's a full URL, extract the filename
    if image_path.startswith('http://') or image_path.startswith('https://'):
        # Extract filename from URL like: http://localhost:4000/static/filename.jpg
        if '/static/' in image_path:
            return image_path.split('/static/')[-1]
        # If URL doesn't have /static/, try to extract last part
        return image_path.split('/')[-1]
    
    # Remove leading slash and 'static/' if exists
    normalized = image_path.lstrip('/')
    if normalized.startswith('static/'):
        normalized = normalized[7:]
    
    return normalized

def _format_image_url(image_path):
    """Format image URL to full URL if needed"""
    if not image_path:
        return None
    
    # If already a full URL (starts with http:// or https://), return as is
    if image_path.startswith('http://') or image_path.startswith('https://'):
        return image_path
    
    # Normalize path (remove leading slash and static/ prefix if exists)
    normalized_path = str(image_path).lstrip('/')
    if normalized_path.startswith('static/'):
        normalized_path = normalized_path[7:]
    
    # If path is empty after normalization, return None
    if not normalized_path:
        return None
    
    # Get API URL from config instance
    config = Config()
    api_url = config.API_URL  # Access property correctly
    result_url = f"{api_url}/static/{normalized_path}"
    print(f"🔗 Formatting image: '{image_path}' -> '{result_url}'")
    return result_url

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
    """Get dishes with pagination (for manage page - shows all dishes)"""
    session = get_session()
    try:
        offset = (page - 1) * limit
        # Get all dishes (for manage page, not filtered by status)
        dishes = session.query(DishModel).order_by(DishModel.created_at.desc()).offset(offset).limit(limit).all()
        
        total_item = session.query(DishModel).count()
        total_page = (total_item + limit - 1) // limit if total_item > 0 else 1
        
        print(f"📄 Pagination request: page={page}, limit={limit}, offset={offset}")
        print(f"📄 Total items: {total_item}, Total pages: {total_page}, Items in this page: {len(dishes)}")
        
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
    from flask import abort
    session = get_session()
    try:
        dish = session.query(DishModel).filter_by(id=dish_id).first()
        if not dish:
            abort(404)
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
        if not body:
            from domain.exceptions import EntityError
            raise EntityError([{'field': 'body', 'message': 'Dữ liệu không hợp lệ'}])
        
        # Validate required fields
        if not body.get('name'):
            from domain.exceptions import EntityError
            raise EntityError([{'field': 'name', 'message': 'Tên món ăn không được để trống'}])
        if not body.get('price') or body.get('price', 0) <= 0:
            from domain.exceptions import EntityError
            raise EntityError([{'field': 'price', 'message': 'Giá phải lớn hơn 0'}])
        
        # Normalize image path before saving to database
        original_image = body.get('image') or ''
        image_path = _normalize_image_path(original_image)
        print(f"🖼️  Original image: {original_image}")
        print(f"🖼️  Normalized image path: {image_path}")
        
        dish = DishModel(
            name=body.get('name', ''),
            price=int(body.get('price', 0)),
            description=body.get('description', ''),
            image=image_path,
            status=body.get('status', 'Available')
        )
        session.add(dish)
        session.commit()
        session.refresh(dish)
        dish_dict = dish.to_dict()
        
        print(f"🖼️  Image from DB: {dish_dict['image']}")
        formatted_image = _format_image_url(dish_dict['image'])
        dish_dict['image'] = formatted_image
        print(f"🖼️  Formatted image URL: {formatted_image}")
        
        print(f"✅ Dish created: ID={dish_dict['id']}, Name={dish_dict['name']}")
        
        # Get updated pagination info for frontend
        total_item = session.query(DishModel).count()
        # Assuming default limit is 10 (can be adjusted)
        default_limit = 10
        total_page = (total_item + default_limit - 1) // default_limit if total_item > 0 else 1
        
        print(f"📊 Pagination: totalItem={total_item}, totalPage={total_page}, currentPage=1")
        
        # Emit socket event to notify frontend about new dish
        try:
            emit_to_manager('new-dish', dish_dict)
            print(f"📡 Socket event 'new-dish' emitted for dish ID={dish_dict['id']}")
        except Exception as e:
            print(f"⚠️  Failed to emit socket event: {str(e)}")
        
        response = jsonify({
            'data': dish_dict,
            'message': 'Tạo món ăn thành công!',
            # Add pagination info so frontend knows to refresh
            'pagination': {
                'totalItem': total_item,
                'totalPage': total_page,
                'currentPage': 1  # New dish will be on page 1 (sorted by created_at DESC)
            }
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        print(f"✅ Response sent for dish ID={dish_dict['id']}")
        return response, 200
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()

def update_dish_service(dish_id, body):
    """Update dish"""
    from flask import abort
    session = get_session()
    try:
        dish = session.query(DishModel).get(dish_id)
        if not dish:
            abort(404)
        dish.name = body.get('name', dish.name)
        dish.price = body.get('price', dish.price)
        dish.description = body.get('description', dish.description)
        # Normalize image path if provided
        if body.get('image') is not None:
            dish.image = _normalize_image_path(body.get('image') or '')
        dish.status = body.get('status', dish.status)
        session.commit()
        session.refresh(dish)
        dish_dict = dish.to_dict()
        dish_dict['image'] = _format_image_url(dish_dict['image'])
        
        # Emit socket event to notify frontend about updated dish
        emit_to_manager('update-dish', dish_dict)
        
        response = jsonify({
            'data': dish_dict,
            'message': 'Cập nhật món ăn thành công!'
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    finally:
        session.close()

def delete_dish_service(dish_id):
    """Delete dish"""
    from flask import abort
    session = get_session()
    try:
        dish = session.query(DishModel).get(dish_id)
        if not dish:
            abort(404)
        dish_dict = dish.to_dict()
        session.delete(dish)
        session.commit()
        
        # Emit socket event to notify frontend about deleted dish
        emit_to_manager('delete-dish', {'id': dish_id})
        
        response = jsonify({
            'data': dish_dict,
            'message': 'Xóa món ăn thành công!'
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    finally:
        session.close()

