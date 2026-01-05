from flask import jsonify
from domain.exceptions import EntityError, AuthError, ForbiddenError, StatusError
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import RequestEntityTooLarge
import os

def setup_error_handler(app):
    """Setup error handler for the app"""
    
    @app.errorhandler(EntityError)
    def handle_entity_error(error):
        response = jsonify({
            'message': 'Lỗi xảy ra khi xác thực dữ liệu...',
            'errors': error.errors,
            'statusCode': 422
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 422
    
    @app.errorhandler(ForbiddenError)
    def handle_forbidden_error(error):
        response = jsonify({
            'message': error.message,
            'statusCode': error.status
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, error.status
    
    @app.errorhandler(AuthError)
    def handle_auth_error(error):
        response = jsonify({
            'message': error.message,
            'statusCode': 401
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 401
    
    @app.errorhandler(StatusError)
    def handle_status_error(error):
        response = jsonify({
            'message': error.message,
            'statusCode': error.status
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, error.status
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        response = jsonify({
            'message': 'Lỗi dữ liệu: Dữ liệu đã tồn tại hoặc không hợp lệ',
            'statusCode': 400
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 400
    
    @app.errorhandler(404)
    def handle_not_found(error):
        # Don't handle 404 for static files - let custom route handle them
        from flask import request
        print(f"🔴 404 Error Handler: path={request.path}")
        app.logger.info(f"🔴 404 Error Handler: path={request.path}")
        
        if request.path.startswith('/static/'):
            # Don't handle static file 404s - let the custom route handle it
            print(f"🔴 Static file 404 - passing through to custom route")
            app.logger.info(f"🔴 Static file 404 - passing through to custom route")
            # Return a proper 404 response for static files (custom route should handle it)
            from werkzeug.exceptions import NotFound
            # Let Flask's default 404 handling work, but return JSON for static files
            response = jsonify({
                'message': f'File not found: {os.path.basename(request.path)}',
                'statusCode': 404
            })
            response.headers['Content-Type'] = 'application/json; charset=utf-8'
            return response, 404
        response = jsonify({
            'message': 'Không tìm thấy dữ liệu',
            'statusCode': 404
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 404
    
    @app.errorhandler(RequestEntityTooLarge)
    def handle_request_entity_too_large(error):
        from config import Config
        max_size_mb = Config.MAX_CONTENT_LENGTH / (1024 * 1024)
        response = jsonify({
            'message': f'File quá lớn. Giới hạn là {max_size_mb:.1f}MB',
            'statusCode': 413,
            'errors': [{'field': 'file', 'message': f'File quá lớn. Giới hạn là {max_size_mb:.1f}MB'}]
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 413
    
    @app.errorhandler(Exception)
    def handle_generic_error(error):
        import traceback
        app.logger.error(f'Unhandled error: {str(error)}')
        app.logger.error(traceback.format_exc())
        response = jsonify({
            'message': str(error) if app.config.get('DEBUG') else 'Lỗi không xác định',
            'statusCode': 500
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 500

