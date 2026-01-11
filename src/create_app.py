from flask import Flask, request
from flask_cors import CORS
from config import Config
from api.routes import register_routes
from api.middleware import setup_middleware
from infrastructure.databases import init_db
from error_handler import setup_error_handler
from utils.helpers import create_folder
from jobs.auto_remove_refresh_token import start_scheduler
from plugins.socket_plugin import init_socketio, setup_socket_handlers
import os

def create_app():
    app = Flask(__name__, static_folder=None, static_url_path=None)  # Disable Flask's default static folder and URL path
    app.config.from_object(Config)
    
    # Set max content length for file uploads
    app.config['MAX_CONTENT_LENGTH'] = Config.MAX_CONTENT_LENGTH
    
    # Ensure UTF-8 encoding for responses
    app.config['JSON_AS_ASCII'] = False  # Allow non-ASCII characters in JSON
    
    # CORS - Configure with all necessary options (including file uploads)
    CORS(app, 
         resources={
             r"/*": {
                 "origins": "*",
                 "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
                 "allow_headers": ["Content-Type", "Authorization", "X-Requested-With"],
                 "expose_headers": ["Content-Type", "Authorization"],
                 "supports_credentials": True,
                 "max_age": 3600
             }
         })
    
    # Disable strict slashes to prevent 308 redirects
    app.url_map.strict_slashes = False
    
    @app.after_request
    def after_request(response):
        # Set charset to UTF-8 for all responses
        content_type = response.headers.get('Content-Type', 'application/json')
        if 'charset' not in content_type.lower():
            if 'application/json' in content_type:
                response.headers['Content-Type'] = 'application/json; charset=utf-8'
            elif 'text/html' in content_type:
                response.headers['Content-Type'] = 'text/html; charset=utf-8'
        # Note: CORS headers are handled by flask_cors.CORS above, don't add them here to avoid duplicates
        return response
    
    # Setup middleware
    setup_middleware(app)
    
    # Setup error handler
    setup_error_handler(app)
    
    # Initialize Socket.IO
    socketio = init_socketio(app)
    setup_socket_handlers(socketio)
    
    # Initialize database
    init_db(app)
    
    # Create upload folder
    upload_folder = app.config.get('UPLOAD_FOLDER', 'uploads')
    create_folder(upload_folder)
    
    # Health check endpoint for keep-alive
    @app.route('/', methods=['GET'])
    @app.route('/health', methods=['GET'])
    def health_check():
        return {'status': 'ok', 'message': 'Server is running'}, 200
    
    # Register routes (static route is registered first in register_routes)
    register_routes(app)
    
    # Verify static route is registered correctly
    print("📋 Registered routes:")
    for rule in app.url_map.iter_rules():
        if '/static' in rule.rule:
            print(f"  - {rule.rule} -> {rule.endpoint}")
    
    # Start background jobs
    start_scheduler()
    
    # Initialize owner account
    with app.app_context():
        from infrastructure.databases import get_session
        from infrastructure.models.account_model import AccountModel
        from utils.crypto_utils import hash_password
        from domain.constants import Role
        
        session = get_session()
        try:
            account_count = session.query(AccountModel).count()
            if account_count == 0:
                hashed_password = hash_password(Config.INITIAL_PASSWORD_OWNER)
                owner = AccountModel(
                    name='Owner',
                    email=Config.INITIAL_EMAIL_OWNER,
                    password=hashed_password,
                    role=Role.Owner
                )
                session.add(owner)
                session.commit()
                print(f"✅ Khởi tạo tài khoản chủ quán thành công: {Config.INITIAL_EMAIL_OWNER}|{Config.INITIAL_PASSWORD_OWNER}")
        except Exception as e:
            print(f"Error initializing owner account: {e}")
            session.rollback()
        finally:
            session.close()
    
    return app, socketio

