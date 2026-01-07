"""
Flask-Admin setup - Prisma Studio style database management
"""
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask import redirect, url_for, request, session
from infrastructure.databases import get_session
from infrastructure.models import (
    AccountModel, DishModel, DishSnapshotModel, TableModel,
    OrderModel, GuestModel, RefreshTokenModel, SocketModel
)
from utils.jwt_utils import verify_access_token
from domain.constants import Role

class SecureModelView(ModelView):
    """ModelView with authentication"""
    
    def is_accessible(self):
        """Check if user is authenticated and is Owner"""
        # Check for token in session (for web interface)
        token = session.get('admin_token')
        
        if not token:
            return False
        
        try:
            decoded = verify_access_token(token)
            role = decoded.get('role')
            return role == Role.Owner
        except:
            return False
    
    def inaccessible_callback(self, name, **kwargs):
        """Redirect to login if not accessible"""
        return redirect('/login')

def setup_admin(app):
    """Setup Flask-Admin"""
    admin = Admin(
        app,
        name='🗄️ Database Studio',
        template_mode='bootstrap4',
        base_template='admin/base.html'
    )
    
    # Get database session
    db_session = get_session()
    
    # Account Model View
    admin.add_view(SecureModelView(
        AccountModel, db_session,
        name='Accounts',
        category='Users'
    ))
    
    # Guest Model View
    admin.add_view(SecureModelView(
        GuestModel, db_session,
        name='Guests',
        category='Users'
    ))
    
    # Dish Model View
    admin.add_view(SecureModelView(
        DishModel, db_session,
        name='Dishes',
        category='Menu'
    ))
    
    # Dish Snapshot Model View
    admin.add_view(SecureModelView(
        DishSnapshotModel, db_session,
        name='Dish Snapshots',
        category='Menu'
    ))
    
    # Table Model View
    admin.add_view(SecureModelView(
        TableModel, db_session,
        name='Tables',
        category='Restaurant'
    ))
    
    # Order Model View
    admin.add_view(SecureModelView(
        OrderModel, db_session,
        name='Orders',
        category='Restaurant'
    ))
    
    # Refresh Token Model View
    admin.add_view(SecureModelView(
        RefreshTokenModel, db_session,
        name='Refresh Tokens',
        category='System'
    ))
    
    # Socket Model View
    admin.add_view(SecureModelView(
        SocketModel, db_session,
        name='Sockets',
        category='System'
    ))
    
    return admin

