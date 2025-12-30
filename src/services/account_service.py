from flask import jsonify, g
from infrastructure.databases import get_session
from infrastructure.models.account_model import AccountModel
from infrastructure.models.socket_model import SocketModel
from infrastructure.models.refresh_token_model import RefreshTokenModel
from utils.crypto_utils import hash_password, compare_password
from utils.jwt_utils import sign_access_token, sign_refresh_token, verify_refresh_token
from domain.exceptions import EntityError
from domain.constants import Role
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from utils.socket_utils import emit_to_socket

def get_account_list_service():
    """Get all accounts"""
    session = get_session()
    try:
        accounts = session.query(AccountModel).order_by(AccountModel.created_at.desc()).all()
        return jsonify({
            'data': [acc.to_dict() for acc in accounts],
            'message': 'Lấy danh sách nhân viên thành công'
        }), 200
    finally:
        session.close()

def create_employee_account_service(body):
    """Create employee account"""
    session = get_session()
    try:
        if body.get('password') != body.get('confirmPassword'):
            raise EntityError([{'field': 'confirmPassword', 'message': 'Mật khẩu không khớp'}])
        
        hashed_password = hash_password(body['password'])
        account = AccountModel(
            name=body['name'],
            email=body['email'],
            password=hashed_password,
            role=Role.Employee,
            avatar=body.get('avatar')
        )
        session.add(account)
        session.commit()
        session.refresh(account)
        return jsonify({
            'data': account.to_dict(),
            'message': 'Tạo tài khoản thành công'
        }), 200
    except IntegrityError:
        session.rollback()
        raise EntityError([{'field': 'email', 'message': 'Email đã tồn tại'}])
    finally:
        session.close()

def get_employee_account_service(account_id):
    """Get employee account by ID"""
    session = get_session()
    try:
        account = session.query(AccountModel).get_or_404(account_id)
        return jsonify({
            'data': account.to_dict(),
            'message': 'Lấy thông tin nhân viên thành công'
        }), 200
    finally:
        session.close()

def update_employee_account_service(account_id, body):
    """Update employee account"""
    session = get_session()
    try:
        socket_record = session.query(SocketModel).filter_by(account_id=account_id).first()
        old_account = session.query(AccountModel).get(account_id)
        
        if not old_account:
            raise EntityError([{'field': 'email', 'message': 'Tài khoản bạn đang cập nhật không còn tồn tại nữa!'}])
        
        is_change_role = old_account.role != body.get('role', old_account.role)
        
        if body.get('changePassword'):
            if body.get('password') != body.get('confirmPassword'):
                raise EntityError([{'field': 'confirmPassword', 'message': 'Mật khẩu không khớp'}])
            hashed_password = hash_password(body['password'])
            old_account.password = hashed_password
        
        old_account.name = body.get('name', old_account.name)
        old_account.email = body.get('email', old_account.email)
        old_account.avatar = body.get('avatar', old_account.avatar)
        old_account.role = body.get('role', old_account.role)
        
        session.commit()
        session.refresh(old_account)
        
        # Emit socket event if role changed
        if is_change_role and socket_record:
            emit_to_socket(socket_record.socket_id, 'refresh-token', old_account.to_dict())
        
        return jsonify({
            'data': old_account.to_dict(),
            'message': 'Cập nhật thành công'
        }), 200
    except IntegrityError:
        session.rollback()
        raise EntityError([{'field': 'email', 'message': 'Email đã tồn tại'}])
    finally:
        session.close()

def delete_employee_account_service(account_id):
    """Delete employee account"""
    session = get_session()
    try:
        socket_record = session.query(SocketModel).filter_by(account_id=account_id).first()
        account = session.query(AccountModel).get_or_404(account_id)
        account_dict = account.to_dict()
        session.delete(account)
        session.commit()
        
        # Emit socket event
        if socket_record:
            emit_to_socket(socket_record.socket_id, 'logout', account_dict)
        
        return jsonify({
            'data': account_dict,
            'message': 'Xóa thành công'
        }), 200
    finally:
        session.close()

def get_me_service():
    """Get current user info"""
    session = get_session()
    try:
        account = session.query(AccountModel).get_or_404(g.current_user_id)
        return jsonify({
            'data': account.to_dict(),
            'message': 'Lấy thông tin thành công'
        }), 200
    finally:
        session.close()

def update_me_service(body):
    """Update current user info"""
    session = get_session()
    try:
        account = session.query(AccountModel).get_or_404(g.current_user_id)
        account.name = body.get('name', account.name)
        account.avatar = body.get('avatar', account.avatar)
        session.commit()
        session.refresh(account)
        return jsonify({
            'data': account.to_dict(),
            'message': 'Cập nhật thông tin thành công'
        }), 200
    finally:
        session.close()

def change_password_service(body):
    """Change password"""
    session = get_session()
    try:
        if body.get('password') != body.get('confirmPassword'):
            raise EntityError([{'field': 'confirmPassword', 'message': 'Mật khẩu mới không khớp'}])
        
        account = session.query(AccountModel).get_or_404(g.current_user_id)
        
        if not compare_password(body['oldPassword'], account.password):
            raise EntityError([{'field': 'oldPassword', 'message': 'Mật khẩu cũ không đúng'}])
        
        account.password = hash_password(body['password'])
        session.commit()
        session.refresh(account)
        return jsonify({
            'data': account.to_dict(),
            'message': 'Đổi mật khẩu thành công'
        }), 200
    finally:
        session.close()

def change_password_v2_service(body):
    """Change password v2 (with new tokens)"""
    session = get_session()
    try:
        if body.get('password') != body.get('confirmPassword'):
            raise EntityError([{'field': 'confirmPassword', 'message': 'Mật khẩu mới không khớp'}])
        
        account = session.query(AccountModel).get_or_404(g.current_user_id)
        
        if not compare_password(body['oldPassword'], account.password):
            raise EntityError([{'field': 'oldPassword', 'message': 'Mật khẩu cũ không đúng'}])
        
        account.password = hash_password(body['password'])
        
        # Delete all refresh tokens
        session.query(RefreshTokenModel).filter_by(account_id=account.id).delete()
        
        # Create new tokens
        access_token = sign_access_token({
            'userId': account.id,
            'role': account.role
        })
        refresh_token = sign_refresh_token({
            'userId': account.id,
            'role': account.role
        })
        
        decoded_refresh_token = verify_refresh_token(refresh_token)
        expires_at = datetime.fromtimestamp(decoded_refresh_token['exp'])
        
        refresh_token_obj = RefreshTokenModel(
            token=refresh_token,
            account_id=account.id,
            expires_at=expires_at
        )
        session.add(refresh_token_obj)
        session.commit()
        session.refresh(account)
        
        return jsonify({
            'message': 'Đổi mật khẩu thành công',
            'data': {
                'account': account.to_dict(),
                'accessToken': access_token,
                'refreshToken': refresh_token
            }
        }), 200
    finally:
        session.close()

def get_guest_list_service(from_date=None, to_date=None):
    """Get guest list"""
    from infrastructure.models.guest_model import GuestModel
    from sqlalchemy import and_
    
    session = get_session()
    try:
        query = session.query(GuestModel)
        if from_date:
            query = query.filter(GuestModel.created_at >= from_date)
        if to_date:
            query = query.filter(GuestModel.created_at <= to_date)
        
        guests = query.order_by(GuestModel.created_at.desc()).all()
        return jsonify({
            'message': 'Lấy danh sách khách thành công',
            'data': [g.to_dict() for g in guests]
        }), 200
    finally:
        session.close()

def create_guest_service(body):
    """Create guest"""
    from infrastructure.models.table_model import TableModel
    from infrastructure.models.guest_model import GuestModel
    from domain.constants import TableStatus
    
    session = get_session()
    try:
        table = session.query(TableModel).get(body['tableNumber'])
        if not table:
            raise EntityError([{'field': 'tableNumber', 'message': 'Bàn không tồn tại'}])
        
        if table.status == TableStatus.Hidden:
            raise EntityError([{'field': 'tableNumber', 'message': f'Bàn {table.number} đã bị ẩn, vui lòng chọn bàn khác'}])
        
        guest = GuestModel(
            name=body['name'],
            table_number=body['tableNumber']
        )
        session.add(guest)
        session.commit()
        session.refresh(guest)
        
        return jsonify({
            'message': 'Tạo tài khoản khách thành công',
            'data': {**guest.to_dict(), 'role': Role.Guest}
        }), 200
    finally:
        session.close()

