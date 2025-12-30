from flask import jsonify
from domain.exceptions import EntityError, AuthError, ForbiddenError, StatusError
from sqlalchemy.exc import IntegrityError

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
        response = jsonify({
            'message': 'Không tìm thấy dữ liệu',
            'statusCode': 404
        })
        response.headers['Content-Type'] = 'application/json; charset=utf-8'
        return response, 404
    
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

