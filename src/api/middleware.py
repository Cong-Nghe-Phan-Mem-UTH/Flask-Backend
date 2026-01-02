from flask import request, jsonify, g
from functools import wraps
from utils.jwt_utils import verify_access_token
from domain.exceptions import AuthError, ForbiddenError
from domain.constants import Role
from config import Config

def require_logined(f):
    """Middleware to require login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            from flask import Response
            return Response(status=200)
        
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise AuthError('Không nhận được access token')
        
        try:
            token = auth_header.split(' ')[1] if ' ' in auth_header else auth_header
            decoded = verify_access_token(token)
            g.current_user_id = decoded.get('userId')
            g.current_user_role = decoded.get('role')
        except ValueError as e:
            raise AuthError('Access token không hợp lệ')
        
        return f(*args, **kwargs)
    return decorated_function

def require_owner(f):
    """Middleware to require Owner role"""
    @wraps(f)
    @require_logined
    def decorated_function(*args, **kwargs):
        if g.current_user_role != Role.Owner:
            raise AuthError('Bạn không có quyền truy cập')
        return f(*args, **kwargs)
    return decorated_function

def require_employee(f):
    """Middleware to require Employee role"""
    @wraps(f)
    @require_logined
    def decorated_function(*args, **kwargs):
        if g.current_user_role != Role.Employee:
            raise AuthError('Bạn không có quyền truy cập')
        return f(*args, **kwargs)
    return decorated_function

def require_guest(f):
    """Middleware to require Guest role"""
    @wraps(f)
    @require_logined
    def decorated_function(*args, **kwargs):
        if g.current_user_role != Role.Guest:
            raise AuthError('Bạn không có quyền truy cập')
        return f(*args, **kwargs)
    return decorated_function

def require_owner_or_employee(f):
    """Middleware to require Owner OR Employee role"""
    @wraps(f)
    @require_logined
    def decorated_function(*args, **kwargs):
        if g.current_user_role not in [Role.Owner, Role.Employee]:
            raise AuthError('Bạn không có quyền truy cập')
        return f(*args, **kwargs)
    return decorated_function

def pause_api_check(f):
    """Check if API is paused"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Skip check for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            from flask import Response
            return Response(status=200)
        
        if Config.PAUSE_SOME_ENDPOINTS:
            raise ForbiddenError('Chức năng bị tạm ngưng')
        return f(*args, **kwargs)
    return decorated_function

def setup_middleware(app):
    """Setup middleware for the app"""
    @app.before_request
    def before_request():
        # Skip authentication for OPTIONS requests (CORS preflight)
        if request.method == 'OPTIONS':
            return

