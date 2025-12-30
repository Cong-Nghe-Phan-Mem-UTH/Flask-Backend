import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def compare_password(password: str, hashed: str) -> bool:
    """Compare password with hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))

