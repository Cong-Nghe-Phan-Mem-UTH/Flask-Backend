from flask_socketio import SocketIO, emit, join_room, disconnect
from flask import request
from infrastructure.databases import get_session
from infrastructure.models.socket_model import SocketModel
from infrastructure.models.account_model import AccountModel
from infrastructure.models.guest_model import GuestModel
from utils.jwt_utils import verify_access_token
from domain.exceptions import AuthError
from domain.constants import Role, ManagerRoom

socketio = None

def init_socketio(app):
    """Initialize Socket.IO"""
    global socketio
    try:
        socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='eventlet',
            logger=True,
            engineio_logger=True
        )
    except:
        # Fallback to threading mode if eventlet not available
        socketio = SocketIO(
            app,
            cors_allowed_origins="*",
            async_mode='threading',
            logger=True,
            engineio_logger=True
        )
    return socketio

def setup_socket_handlers(socketio):
    """Setup Socket.IO handlers"""
    
    @socketio.on('connect')
    def handle_connect(auth):
        """Handle socket connection"""
        try:
            authorization = auth.get('Authorization') if auth else None
            
            if not authorization:
                print('❌ Socket connection: No authorization')
                return False
            
            token = authorization.split(' ')[1] if ' ' in authorization else authorization
            decoded_access_token = verify_access_token(token)
            user_id = decoded_access_token.get('userId')
            role = decoded_access_token.get('role')
            
            session = get_session()
            try:
                if role == Role.Guest:
                    # Upsert socket for guest
                    socket_record = session.query(SocketModel).filter_by(guest_id=user_id).first()
                    if socket_record:
                        socket_record.socket_id = request.sid
                    else:
                        socket_record = SocketModel(
                            guest_id=user_id,
                            socket_id=request.sid
                        )
                        session.add(socket_record)
                else:
                    # Upsert socket for account
                    socket_record = session.query(SocketModel).filter_by(account_id=user_id).first()
                    if socket_record:
                        socket_record.socket_id = request.sid
                    else:
                        socket_record = SocketModel(
                            account_id=user_id,
                            socket_id=request.sid
                        )
                        session.add(socket_record)
                    # Join manager room
                    join_room(ManagerRoom)
                
                session.commit()
                print(f'🔌 Socket connected: {request.sid} (User: {user_id}, Role: {role})')
                return True
            except Exception as e:
                session.rollback()
                print(f'❌ Socket connection error: {str(e)}')
                return False
            finally:
                session.close()
        except Exception as e:
            print(f'❌ Socket connection error: {str(e)}')
            return False
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle socket disconnection"""
        print(f'🔌 Socket disconnected: {request.sid}')

def get_socketio():
    """Get Socket.IO instance"""
    return socketio

