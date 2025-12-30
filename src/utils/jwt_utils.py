import jwt
from datetime import datetime, timedelta
from config import Config
from typing import Dict, Optional

def parse_time_string(time_str: str) -> timedelta:
    """Parse time string like '15m', '7d', '1h' to timedelta"""
    if not time_str:
        return timedelta(minutes=15)
    
    time_str = time_str.lower().strip()
    try:
        if time_str.endswith('m'):
            minutes = int(time_str[:-1])
            return timedelta(minutes=minutes)
        elif time_str.endswith('h'):
            hours = int(time_str[:-1])
            return timedelta(hours=hours)
        elif time_str.endswith('d'):
            days = int(time_str[:-1])
            return timedelta(days=days)
        elif time_str.endswith('s'):
            seconds = int(time_str[:-1])
            return timedelta(seconds=seconds)
        else:
            # Try to parse as number (default to minutes)
            num = int(time_str)
            return timedelta(minutes=num)
    except (ValueError, AttributeError):
        return timedelta(minutes=15)

def sign_access_token(payload: Dict, expires_in: Optional[timedelta] = None) -> str:
    """Sign access token"""
    if expires_in is None:
        expires_in = parse_time_string(Config.ACCESS_TOKEN_EXPIRES_IN)
    
    payload['tokenType'] = 'AccessToken'
    payload['exp'] = datetime.utcnow() + expires_in
    payload['iat'] = datetime.utcnow()
    
    return jwt.encode(payload, Config.ACCESS_TOKEN_SECRET, algorithm='HS256')

def sign_refresh_token(payload: Dict, expires_in: Optional[timedelta] = None) -> str:
    """Sign refresh token"""
    if expires_in is None:
        expires_in = parse_time_string(Config.REFRESH_TOKEN_EXPIRES_IN)
    
    payload['tokenType'] = 'RefreshToken'
    payload['exp'] = datetime.utcnow() + expires_in
    payload['iat'] = datetime.utcnow()
    
    return jwt.encode(payload, Config.REFRESH_TOKEN_SECRET, algorithm='HS256')

def verify_access_token(token: str) -> Dict:
    """Verify access token"""
    try:
        decoded = jwt.decode(token, Config.ACCESS_TOKEN_SECRET, algorithms=['HS256'])
        if decoded.get('tokenType') != 'AccessToken':
            raise ValueError('Invalid token type')
        return decoded
    except jwt.ExpiredSignatureError:
        raise ValueError('Token expired')
    except jwt.InvalidTokenError:
        raise ValueError('Invalid token')

def verify_refresh_token(token: str) -> Dict:
    """Verify refresh token"""
    try:
        decoded = jwt.decode(token, Config.REFRESH_TOKEN_SECRET, algorithms=['HS256'])
        if decoded.get('tokenType') != 'RefreshToken':
            raise ValueError('Invalid token type')
        return decoded
    except jwt.ExpiredSignatureError:
        raise ValueError('Token expired')
    except jwt.InvalidTokenError:
        raise ValueError('Invalid token')

