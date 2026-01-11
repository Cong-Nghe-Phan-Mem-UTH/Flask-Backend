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
    # Handle None, empty string, or whitespace-only strings
    if not image_path or (isinstance(image_path, str) and not image_path.strip()):
        print(f"⚠️  Empty or None image path, returning None")
        return None
    
    # Convert to string and strip whitespace
    image_path = str(image_path).strip()
    
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
        normalized_path = image_path.lstrip('/')
        if normalized_path.startswith('static/'):
            normalized_path = normalized_path[7:]
    
    # If path is empty after normalization, return None
    if not normalized_path or not normalized_path.strip():
        print(f"⚠️  Image path became empty after normalization: '{image_path}' -> '{normalized_path}'")
        return None
    
    # Get API URL from config instance
    config = Config()
    api_url = config.API_URL  # Access property correctly
    result_url = f"{api_url}/static/{normalized_path}"
    print(f"🔗 Formatting image: '{image_path}' -> '{result_url}'")
    return result_url

def get_dish_list_service(show_all=False, include_unavailable=False):
    """Get all dishes (for public homepage)
    
    Args:
        show_all: If True, show all dishes regardless of status
        include_unavailable: If True, include Unavailable dishes (but still exclude Hidden)
    """
    session = get_session()
    try:
        # If show_all is True, return all dishes
        if show_all:
            dishes = session.query(DishModel).order_by(DishModel.created_at.desc()).all()
        elif include_unavailable:
            # Show Available and Unavailable, but exclude Hidden
            dishes = session.query(DishModel).filter(
                DishModel.status.in_(['Available', 'Unavailable'])
            ).order_by(DishModel.created_at.desc()).all()
        else:
            # Default: Get all dishes, but prioritize Available ones
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
            original_image = dish_dict.get('image')
            formatted_image = _format_image_url(original_image)
            dish_dict['image'] = formatted_image
            print(f"📸 Dish ID {dish.id} ({dish.name}): original='{original_image}' -> formatted='{formatted_image}'")
            dishes_data.append(dish_dict)
        
        # Get status counts for frontend info
        total_count = session.query(DishModel).count()
        available_count = session.query(DishModel).filter(DishModel.status == 'Available').count()
        unavailable_count = session.query(DishModel).filter(DishModel.status == 'Unavailable').count()
        hidden_count = session.query(DishModel).filter(DishModel.status == 'Hidden').count()
        
        response = jsonify({
            'data': dishes_data,
            'message': 'Lấy danh sách món ăn thành công!',
            'stats': {
                'total': total_count,
                'available': available_count,
                'unavailable': unavailable_count,
                'hidden': hidden_count,
                'showing': len(dishes_data)
            },
            'filters': {
                'showAll': show_all,
                'includeUnavailable': include_unavailable
            }
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    finally:
        session.close()

def get_dish_list_with_pagination_service(page, limit):
    """Get dishes with pagination (for manage page - shows all dishes including Unavailable/Hidden)"""
    session = get_session()
    try:
        offset = (page - 1) * limit
        # Get all dishes (for manage page, not filtered by status - includes Unavailable and Hidden)
        dishes = session.query(DishModel).order_by(DishModel.created_at.desc()).offset(offset).limit(limit).all()
        
        total_item = session.query(DishModel).count()
        total_page = (total_item + limit - 1) // limit if total_item > 0 else 1
        
        # Get status breakdown for logging
        available_count = session.query(DishModel).filter(DishModel.status == 'Available').count()
        unavailable_count = session.query(DishModel).filter(DishModel.status == 'Unavailable').count()
        hidden_count = session.query(DishModel).filter(DishModel.status == 'Hidden').count()
        
        print(f"📄 Pagination request: page={page}, limit={limit}, offset={offset}")
        print(f"📄 Total items: {total_item} (Available: {available_count}, Unavailable: {unavailable_count}, Hidden: {hidden_count})")
        print(f"📄 Total pages: {total_page}, Items in this page: {len(dishes)}")
        
        # Log status of dishes in current page
        status_breakdown = {}
        for dish in dishes:
            status = dish.status
            status_breakdown[status] = status_breakdown.get(status, 0) + 1
        print(f"📄 Status in current page: {status_breakdown}")
        
        # Format dishes with full image URLs
        dishes_data = []
        for dish in dishes:
            dish_dict = dish.to_dict()
            original_image = dish_dict.get('image')
            formatted_image = _format_image_url(original_image)
            dish_dict['image'] = formatted_image
            print(f"📸 Dish ID {dish.id} ({dish.name}): original='{original_image}' -> formatted='{formatted_image}'")
            dishes_data.append(dish_dict)
        
        response = jsonify({
            'data': {
                'items': dishes_data,
                'totalItem': total_item,
                'totalPage': total_page,
                'page': page,
                'limit': limit
            },
            'message': 'Lấy danh sách món ăn thành công!',
            'stats': {
                'total': total_item,
                'available': available_count,
                'unavailable': unavailable_count,
                'hidden': hidden_count
            }
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
        
        # Get status from body, default to 'Available'
        dish_status = body.get('status', 'Available')
        print(f"📝 Creating dish with status: {dish_status}")
        
        dish = DishModel(
            name=body.get('name', ''),
            price=int(body.get('price', 0)),
            description=body.get('description', ''),
            image=image_path,
            status=dish_status
        )
        session.add(dish)
        session.commit()
        session.refresh(dish)
        dish_dict = dish.to_dict()
        
        print(f"🖼️  Image from DB: {dish_dict['image']}")
        formatted_image = _format_image_url(dish_dict['image'])
        dish_dict['image'] = formatted_image
        print(f"🖼️  Formatted image URL: {formatted_image}")
        
        print(f"✅ Dish created: ID={dish_dict['id']}, Name={dish_dict['name']}, Status={dish_dict['status']}")
        
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
                'currentPage': 1,  # New dish will be on page 1 (sorted by created_at DESC)
                'limit': default_limit
            },
            # Add flag to indicate frontend should refresh
            'shouldRefresh': True,
            'newDishId': dish_dict['id']
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
        if not body:
            from domain.exceptions import EntityError
            raise EntityError([{'field': 'body', 'message': 'Dữ liệu không hợp lệ'}])
        
        dish = session.query(DishModel).get(dish_id)
        if not dish:
            abort(404)
        
        # Validate required fields if provided
        if 'name' in body and not body.get('name'):
            from domain.exceptions import EntityError
            raise EntityError([{'field': 'name', 'message': 'Tên món ăn không được để trống'}])
        
        if 'price' in body and (not body.get('price') or body.get('price', 0) <= 0):
            from domain.exceptions import EntityError
            raise EntityError([{'field': 'price', 'message': 'Giá phải lớn hơn 0'}])
        
        # Update fields
        if 'name' in body:
            dish.name = body.get('name')
        if 'price' in body:
            dish.price = int(body.get('price'))
        if 'description' in body:
            dish.description = body.get('description')
        
        # Normalize image path if provided
        if 'image' in body:
            original_image = body.get('image') or ''
            image_path = _normalize_image_path(original_image)
            print(f"🖼️  Update dish - Original image: {original_image}")
            print(f"🖼️  Update dish - Normalized image path: {image_path}")
            dish.image = image_path
        
        if 'status' in body:
            dish.status = body.get('status')
        
        session.commit()
        session.refresh(dish)
        dish_dict = dish.to_dict()
        dish_dict['image'] = _format_image_url(dish_dict['image'])
        
        print(f"✅ Dish updated: ID={dish_dict['id']}, Name={dish_dict['name']}, Image={dish_dict['image']}")
        
        # Emit socket event to notify frontend about updated dish
        emit_to_manager('update-dish', dish_dict)
        
        response = jsonify({
            'data': dish_dict,
            'message': 'Cập nhật món ăn thành công!'
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except Exception as e:
        session.rollback()
        current_app.logger.error(f"❌ Error updating dish {dish_id}: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        # Re-raise domain exceptions (EntityError, AuthError, etc.) to be handled by error handlers
        from domain.exceptions import EntityError, AuthError, ForbiddenError, StatusError
        if isinstance(e, (EntityError, AuthError, ForbiddenError, StatusError)):
            raise
        # Re-raise HTTP exceptions (404, etc.) to be handled by Flask
        from werkzeug.exceptions import HTTPException
        if isinstance(e, HTTPException):
            raise
        # Convert other errors to EntityError with specific message
        from domain.exceptions import EntityError
        error_message = str(e) if str(e) else 'Lỗi không xác định'
        raise EntityError([{'field': 'general', 'message': f'Lỗi khi cập nhật món ăn: {error_message}'}])
    finally:
        session.close()

def delete_dish_service(dish_id, force_delete=False):
    """Delete dish
    
    Args:
        dish_id: ID of the dish to delete
        force_delete: If True, delete related orders and dish snapshots. If False, prevent deletion if orders exist.
    """
    from flask import abort
    from infrastructure.models.order_model import OrderModel
    from sqlalchemy.exc import IntegrityError
    from domain.exceptions import EntityError, AuthError, ForbiddenError, StatusError
    from werkzeug.exceptions import HTTPException
    
    session = get_session()
    try:
        dish = session.query(DishModel).get(dish_id)
        if not dish:
            abort(404)
        
        # Check if there are any orders referencing this dish's snapshots
        dish_snapshot_ids = [snapshot.id for snapshot in dish.dish_snapshots]
        orders_count = 0
        if dish_snapshot_ids:
            orders_count = session.query(OrderModel).filter(
                OrderModel.dish_snapshot_id.in_(dish_snapshot_ids)
            ).count()
            
            if orders_count > 0 and not force_delete:
                # Cannot delete dish because it has orders (unless force delete)
                raise EntityError([{
                    'field': 'general', 
                    'message': f'Không thể xóa món ăn này vì có {orders_count} đơn hàng đang tham chiếu đến nó. Vui lòng xóa hoặc xử lý các đơn hàng trước, hoặc sử dụng force delete để xóa cả đơn hàng liên quan.'
                }])
            
            # If force delete, delete related orders first
            if force_delete and orders_count > 0:
                deleted_orders = session.query(OrderModel).filter(
                    OrderModel.dish_snapshot_id.in_(dish_snapshot_ids)
                ).all()
                for order in deleted_orders:
                    session.delete(order)
                current_app.logger.info(f"🗑️  Force delete: Deleted {orders_count} orders related to dish {dish_id}")
        
        dish_dict = dish.to_dict()
        session.delete(dish)
        session.commit()
        
        # Emit socket event to notify frontend about deleted dish
        emit_to_manager('delete-dish', {'id': dish_id})
        
        message = 'Xóa món ăn thành công!'
        if force_delete and orders_count > 0:
            message = f'Xóa món ăn thành công! Đã xóa {orders_count} đơn hàng liên quan.'
        
        response = jsonify({
            'data': dish_dict,
            'message': message,
            'deletedOrdersCount': orders_count if force_delete else 0
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 200
    except (EntityError, AuthError, ForbiddenError, StatusError):
        session.rollback()
        raise
    except HTTPException:
        session.rollback()
        raise
    except IntegrityError as e:
        session.rollback()
        current_app.logger.error(f"❌ IntegrityError when deleting dish {dish_id}: {str(e)}")
        # Check if it's a foreign key constraint issue
        error_msg = str(e).lower()
        if 'foreign key' in error_msg or 'constraint' in error_msg:
            raise EntityError([{
                'field': 'general', 
                'message': 'Không thể xóa món ăn này vì có dữ liệu khác đang tham chiếu đến nó (đơn hàng, v.v.). Vui lòng xóa các dữ liệu liên quan trước.'
            }])
        # Re-raise other IntegrityErrors to be handled by error handler
        raise
    except Exception as e:
        session.rollback()
        current_app.logger.error(f"❌ Error deleting dish {dish_id}: {str(e)}")
        import traceback
        current_app.logger.error(traceback.format_exc())
        # Convert other errors to EntityError
        raise EntityError([{'field': 'general', 'message': f'Lỗi khi xóa món ăn: {str(e)}'}])
    finally:
        session.close()

