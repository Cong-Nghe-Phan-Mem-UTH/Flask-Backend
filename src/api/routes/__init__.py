# Routes package
from api.auth.auth_routes import auth_bp
from api.routes.account_routes import account_bp
from api.routes.dish_routes import dish_bp
from api.routes.table_routes import table_bp
from api.routes.order_routes import order_bp
from api.routes.guest_routes import guest_bp
from api.routes.media_routes import media_bp
from api.routes.static_routes import static_bp
from api.routes.test_routes import test_bp
from api.routes.indicator_routes import indicator_bp
from api.routes.admin_routes import admin_bp

def register_routes(app):
    # Register static route FIRST to override Flask's default static route
    app.register_blueprint(static_bp, url_prefix="/static")
    
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(account_bp, url_prefix="/accounts")
    app.register_blueprint(dish_bp, url_prefix="/dishes")
    app.register_blueprint(table_bp, url_prefix="/tables")
    app.register_blueprint(order_bp, url_prefix="/orders")
    app.register_blueprint(guest_bp, url_prefix="/guest")
    app.register_blueprint(media_bp, url_prefix="/media")
    app.register_blueprint(test_bp, url_prefix="/test")
    app.register_blueprint(indicator_bp, url_prefix="/indicators")
    app.register_blueprint(admin_bp, url_prefix="/admin")

