"""
Prisma Studio style admin panel - runs on port 5555
Similar to Prisma Studio for database management
"""
from flask import Flask, request, session, redirect, url_for, render_template_string
from flask_cors import CORS
from config import Config
from infrastructure.databases import init_db
from infrastructure.admin_setup import setup_admin
from utils.jwt_utils import verify_access_token
from domain.constants import Role
import os

def create_admin_app():
    """Create Flask app for admin panel"""
    app = Flask(__name__)
    app.config.from_object(Config)
    app.config['SECRET_KEY'] = Config.SECRET_KEY
    app.config['JSON_AS_ASCII'] = False
    
    # CORS for admin panel
    CORS(app, resources={r"/*": {"origins": "*"}})
    
    # Initialize database
    init_db(app)
    
    # Setup Flask-Admin
    setup_admin(app)
    
    # Root route - redirect to login
    @app.route('/')
    def root():
        """Root route - redirect to login"""
        return redirect('/login')
    
    # Admin login route
    @app.route('/login', methods=['GET', 'POST'])
    def admin_login():
        """Admin login page"""
        if request.method == 'POST':
            email = request.form.get('email')
            password = request.form.get('password')
            
            # Authenticate directly
            from infrastructure.databases import get_session
            from infrastructure.models.account_model import AccountModel
            from utils.crypto_utils import compare_password
            from utils.jwt_utils import sign_access_token
            
            session_db = get_session()
            try:
                account = session_db.query(AccountModel).filter_by(email=email).first()
                
                if not account:
                    return render_template_string(LOGIN_HTML, error='Email không tồn tại')
                
                if not compare_password(password, account.password):
                    return render_template_string(LOGIN_HTML, error='Email hoặc mật khẩu không đúng')
                
                # Check if Owner
                if account.role != Role.Owner:
                    return render_template_string(LOGIN_HTML, error='Chỉ Owner mới có quyền truy cập')
                
                # Generate token
                token = sign_access_token({
                    'userId': account.id,
                    'role': account.role
                })
                
                session['admin_token'] = token
                return redirect('/admin')
            except Exception as e:
                return render_template_string(LOGIN_HTML, error=f'Error: {str(e)}')
            finally:
                session_db.close()
        
        return render_template_string(LOGIN_HTML)
    
    @app.route('/logout')
    def admin_logout():
        """Admin logout"""
        session.pop('admin_token', None)
        return redirect('/login')
    
    return app

LOGIN_HTML = """
<!DOCTYPE html>
<html lang="vi">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Admin Login - Database Studio</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #e0e0e0;
            display: flex;
            justify-content: center;
            align-items: center;
            min-height: 100vh;
        }
        .login-container {
            background: #2a2a2a;
            border: 1px solid #3a3a3a;
            border-radius: 12px;
            padding: 40px;
            width: 100%;
            max-width: 400px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
        }
        h1 {
            color: #fff;
            margin-bottom: 10px;
            font-size: 28px;
            text-align: center;
        }
        .subtitle {
            color: #888;
            text-align: center;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #e0e0e0;
            font-size: 14px;
        }
        input {
            width: 100%;
            padding: 12px;
            background: #1a1a1a;
            border: 1px solid #3a3a3a;
            border-radius: 6px;
            color: #e0e0e0;
            font-size: 14px;
        }
        input:focus {
            outline: none;
            border-color: #667eea;
        }
        .btn {
            width: 100%;
            padding: 12px;
            background: #667eea;
            color: white;
            border: none;
            border-radius: 6px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: background 0.2s;
        }
        .btn:hover {
            background: #5568d3;
        }
        .error {
            color: #ff4444;
            margin-top: 10px;
            font-size: 14px;
            text-align: center;
        }
    </style>
</head>
<body>
    <div class="login-container">
        <h1>🗄️ Database Studio</h1>
        <p class="subtitle">Prisma Studio Style - Owner Login Required</p>
        <form method="POST">
            <div class="form-group">
                <label>Email</label>
                <input type="email" name="email" required placeholder="admin@order.com">
            </div>
            <div class="form-group">
                <label>Password</label>
                <input type="password" name="password" required placeholder="123456">
            </div>
            <button type="submit" class="btn">Login</button>
            {% if error %}
            <div class="error">{{ error }}</div>
            {% endif %}
        </form>
    </div>
</body>
</html>
"""

if __name__ == '__main__':
    try:
        app = create_admin_app()
        port = int(os.environ.get('ADMIN_PORT', 5555))
        print(f"🚀 Database Studio (Prisma Studio style) running on http://localhost:{port}")
        print(f"📊 Access admin panel at: http://localhost:{port}/admin")
        print(f"🔐 Login at: http://localhost:{port}/login")
        print(f"🏠 Root URL: http://localhost:{port}/")
        app.run(host='0.0.0.0', port=port, debug=True)
    except Exception as e:
        print(f"❌ Error starting Database Studio: {e}")
        import traceback
        traceback.print_exc()

