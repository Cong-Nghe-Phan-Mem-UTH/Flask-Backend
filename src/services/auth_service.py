from flask import jsonify, redirect
from infrastructure.databases import get_session
from infrastructure.models.account_model import AccountModel
from infrastructure.models.refresh_token_model import RefreshTokenModel
from utils.crypto_utils import compare_password
from utils.jwt_utils import sign_access_token, sign_refresh_token, verify_refresh_token
from domain.exceptions import EntityError, AuthError, StatusError
from domain.constants import Role
from datetime import datetime
import requests
from config import Config

def login_service(body):
    """Handle login"""
    session = get_session()
    try:
        email = body.get("email")
        password = body.get("password")
        
        account = session.query(AccountModel).filter_by(email=email).first()
        
        if not account:
            raise EntityError([{'field': 'email', 'message': 'Email không tồn tại'}])
        
        if not compare_password(password, account.password):
            raise EntityError([{'field': 'password', 'message': 'Email hoặc mật khẩu không đúng'}])
        
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
        
        # Save refresh token
        refresh_token_obj = RefreshTokenModel(
            token=refresh_token,
            account_id=account.id,
            expires_at=expires_at
        )
        session.add(refresh_token_obj)
        session.commit()
        
        return jsonify({
            "message": "Đăng nhập thành công",
            "data": {
                "account": account.to_dict(),
                "accessToken": access_token,
                "refreshToken": refresh_token
            }
        }), 200
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def refresh_token_service(body):
    """Handle refresh token"""
    session = get_session()
    try:
        refresh_token = body.get("refreshToken")
        
        try:
            decoded = verify_refresh_token(refresh_token)
        except ValueError:
            raise AuthError('Refresh token không hợp lệ')
        
        refresh_token_obj = session.query(RefreshTokenModel).filter_by(token=refresh_token).first()
        if not refresh_token_obj:
            raise AuthError('Refresh token không tồn tại')
        
        account = session.query(AccountModel).get(refresh_token_obj.account_id)
        if not account:
            raise AuthError('Tài khoản không tồn tại')
        
        new_access_token = sign_access_token({
            'userId': account.id,
            'role': account.role
        })
        
        new_refresh_token = sign_refresh_token({
            'userId': account.id,
            'role': account.role,
            'exp': decoded.get('exp')
        })
        
        # Delete old and create new refresh token
        session.delete(refresh_token_obj)
        
        decoded_new_refresh = verify_refresh_token(new_refresh_token)
        expires_at = datetime.fromtimestamp(decoded_new_refresh['exp'])
        
        new_refresh_token_obj = RefreshTokenModel(
            token=new_refresh_token,
            account_id=account.id,
            expires_at=expires_at
        )
        session.add(new_refresh_token_obj)
        session.commit()
        
        return jsonify({
            "message": "Lấy token mới thành công",
            "data": {
                "accessToken": new_access_token,
                "refreshToken": new_refresh_token
            }
        }), 200
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def logout_service(body):
    """Handle logout"""
    session = get_session()
    try:
        refresh_token = body.get("refreshToken")
        refresh_token_obj = session.query(RefreshTokenModel).filter_by(token=refresh_token).first()
        if refresh_token_obj:
            session.delete(refresh_token_obj)
            session.commit()
        return jsonify({"message": "Đăng xuất thành công"}), 200
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()

def login_google_service(code):
    """Handle Google OAuth login"""
    if not code:
        return jsonify({"message": "Thiếu code"}), 400
    
    session = get_session()
    try:
        # Get OAuth token from Google
        token_data = {
            'code': code,
            'client_id': Config.GOOGLE_CLIENT_ID,
            'client_secret': Config.GOOGLE_CLIENT_SECRET,
            'redirect_uri': Config.GOOGLE_AUTHORIZED_REDIRECT_URI,
            'grant_type': 'authorization_code'
        }
        
        token_response = requests.post(
            'https://oauth2.googleapis.com/token',
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'}
        )
        token_response.raise_for_status()
        token_json = token_response.json()
        
        # Get user info from Google
        user_response = requests.get(
            'https://www.googleapis.com/oauth2/v1/userinfo',
            params={'access_token': token_json['access_token'], 'alt': 'json'},
            headers={'Authorization': f"Bearer {token_json['id_token']}"}
        )
        user_response.raise_for_status()
        google_user = user_response.json()
        
        if not google_user.get('verified_email'):
            raise StatusError('Email chưa được xác minh từ Google', 403)
        
        account = session.query(AccountModel).filter_by(email=google_user['email']).first()
        if not account:
            raise StatusError('Tài khoản này không tồn tại trên hệ thống website', 403)
        
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
        
        return redirect(f"{Config.GOOGLE_REDIRECT_CLIENT_URL}?accessToken={access_token}&refreshToken={refresh_token}&status=200")
    except Exception as e:
        session.rollback()
        if isinstance(e, StatusError):
            return redirect(f"{Config.GOOGLE_REDIRECT_CLIENT_URL}?message={e.message}&status={e.status}")
        return redirect(f"{Config.GOOGLE_REDIRECT_CLIENT_URL}?message=Lỗi không xác định&status=500")
    finally:
        session.close()

