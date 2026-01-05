from flask import Blueprint, render_template_string, request, jsonify, g
from api.middleware import require_owner
from infrastructure.databases import get_session, engine
from infrastructure.databases.base import Base
from infrastructure.models import (
    AccountModel, DishModel, DishSnapshotModel, TableModel, 
    OrderModel, GuestModel, RefreshTokenModel, SocketModel
)
from sqlalchemy import inspect, text
import json

admin_bp = Blueprint('admin', __name__)

# Map table names to models
TABLE_MODELS = {
    'Account': AccountModel,
    'Dish': DishModel,
    'DishSnapshot': DishSnapshotModel,
    'Table': TableModel,
    'Order': OrderModel,
    'Guest': GuestModel,
    'RefreshToken': RefreshTokenModel,
    'Socket': SocketModel,
}

def serialize_value(value):
    """Serialize value for JSON response"""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return value
    if hasattr(value, 'isoformat'):  # datetime
        try:
            return value.isoformat()
        except:
            return str(value)
    # Handle other types
    try:
        return json.dumps(value, default=str)
    except:
        return str(value)

@admin_bp.route('/login')
def admin_login():
    """Admin login page"""
    html = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Admin Login - Database Admin</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: #1a1a1a;
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
            }
            h1 {
                color: #fff;
                margin-bottom: 10px;
                font-size: 24px;
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
                border-color: #4a9eff;
            }
            .btn {
                width: 100%;
                padding: 12px;
                background: #4a9eff;
                color: white;
                border: none;
                border-radius: 6px;
                font-size: 16px;
                font-weight: 600;
                cursor: pointer;
                transition: background 0.2s;
            }
            .btn:hover {
                background: #3a8eef;
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
            <h1>🗄️ Database Admin</h1>
            <p class="subtitle">Owner Login Required</p>
            <form id="loginForm">
                <div class="form-group">
                    <label>Email</label>
                    <input type="email" id="email" required placeholder="admin@order.com">
                </div>
                <div class="form-group">
                    <label>Password</label>
                    <input type="password" id="password" required placeholder="123456">
                </div>
                <button type="submit" class="btn">Login</button>
                <div id="error" class="error"></div>
            </form>
        </div>
        <script>
            document.getElementById('loginForm').addEventListener('submit', async (e) => {
                e.preventDefault();
                const email = document.getElementById('email').value;
                const password = document.getElementById('password').value;
                const errorDiv = document.getElementById('error');
                errorDiv.textContent = '';
                
                try {
                    const res = await fetch('/auth/login', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ email, password })
                    });
                    
                    const data = await res.json();
                    
                    if (res.ok && data.data && data.data.accessToken) {
                        localStorage.setItem('admin_token', data.data.accessToken);
                        window.location.href = '/admin/';
                    } else {
                        errorDiv.textContent = data.message || 'Login failed';
                    }
                } catch (err) {
                    errorDiv.textContent = 'Error: ' + err.message;
                }
            });
        </script>
    </body>
    </html>
    """
    return html

@admin_bp.route('/')
def admin_home():
    """Admin home page - list all tables"""
    html = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Database Admin - Prisma Studio Style</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: #1a1a1a;
                color: #e0e0e0;
                padding: 20px;
            }
            .container {
                max-width: 1400px;
                margin: 0 auto;
            }
            h1 {
                color: #fff;
                margin-bottom: 30px;
                font-size: 28px;
            }
            .tables-grid {
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                gap: 15px;
            }
            .table-card {
                background: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 20px;
                cursor: pointer;
                transition: all 0.2s;
                text-decoration: none;
                color: inherit;
                display: block;
            }
            .table-card:hover {
                background: #3a3a3a;
                border-color: #4a9eff;
                transform: translateY(-2px);
            }
            .table-name {
                font-size: 18px;
                font-weight: 600;
                margin-bottom: 8px;
                color: #4a9eff;
            }
            .table-count {
                color: #888;
                font-size: 14px;
            }
            .back-btn {
                display: inline-block;
                margin-bottom: 20px;
                padding: 10px 20px;
                background: #4a9eff;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                transition: background 0.2s;
            }
            .back-btn:hover {
                background: #3a8eef;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
                <h1>🗄️ Database Admin</h1>
                <button onclick="logout()" style="padding: 10px 20px; background: #ff4444; color: white; border: none; border-radius: 6px; cursor: pointer;">Logout</button>
            </div>
            <div class="tables-grid" id="tablesGrid">
                Loading...
            </div>
        </div>
        <script>
            function logout() {
                localStorage.removeItem('admin_token');
                window.location.href = '/admin/login';
            }
        </script>
        <script>
            const token = localStorage.getItem('admin_token');
            if (!token) {
                window.location.href = '/admin/login';
            }
            
            fetch('/admin/api/tables', {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            })
                .then(r => {
                    if (r.status === 401) {
                        localStorage.removeItem('admin_token');
                        window.location.href = '/admin/login';
                        return;
                    }
                    return r.json();
                })
                .then(data => {
                    if (!data) return;
                    const grid = document.getElementById('tablesGrid');
                    grid.innerHTML = data.tables.map(table => `
                        <a href="/admin/table/${table.name}" class="table-card">
                            <div class="table-name">${table.name}</div>
                            <div class="table-count">${table.count} records</div>
                        </a>
                    `).join('');
                })
                .catch(err => {
                    document.getElementById('tablesGrid').innerHTML = '<p style="color: #ff4444;">Error loading tables</p>';
                });
        </script>
    </body>
    </html>
    """
    return html

@admin_bp.route('/api/tables')
@require_owner
def get_tables():
    """Get list of all tables with record counts"""
    session = get_session()
    try:
        tables = []
        for table_name, model in TABLE_MODELS.items():
            count = session.query(model).count()
            tables.append({
                'name': table_name,
                'count': count
            })
        return jsonify({'tables': tables})
    finally:
        session.close()

@admin_bp.route('/table/<table_name>')
def view_table(table_name):
    """View table data"""
    if table_name not in TABLE_MODELS:
        return "Table not found", 404
    
    html_template = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{{ table_name }} - Database Admin</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: #1a1a1a;
                color: #e0e0e0;
                padding: 20px;
            }
            .container {
                max-width: 1600px;
                margin: 0 auto;
            }
            .header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            h1 {
                color: #fff;
                font-size: 28px;
            }
            .back-btn {
                padding: 10px 20px;
                background: #4a9eff;
                color: white;
                text-decoration: none;
                border-radius: 6px;
                transition: background 0.2s;
            }
            .back-btn:hover {
                background: #3a8eef;
            }
            .controls {
                margin-bottom: 20px;
                display: flex;
                gap: 10px;
                flex-wrap: wrap;
            }
            .search-input {
                flex: 1;
                min-width: 200px;
                padding: 10px;
                background: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                color: #e0e0e0;
                font-size: 14px;
            }
            .search-input:focus {
                outline: none;
                border-color: #4a9eff;
            }
            .table-wrapper {
                background: #2a2a2a;
                border-radius: 8px;
                overflow: hidden;
                overflow-x: auto;
            }
            table {
                width: 100%;
                border-collapse: collapse;
            }
            th {
                background: #1a1a1a;
                padding: 12px;
                text-align: left;
                font-weight: 600;
                color: #4a9eff;
                border-bottom: 2px solid #3a3a3a;
                position: sticky;
                top: 0;
            }
            td {
                padding: 12px;
                border-bottom: 1px solid #3a3a3a;
            }
            tr:hover {
                background: #3a3a3a;
            }
            .empty {
                text-align: center;
                padding: 40px;
                color: #888;
            }
            .pagination {
                margin-top: 20px;
                display: flex;
                justify-content: center;
                gap: 10px;
            }
            .page-btn {
                padding: 8px 16px;
                background: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                color: #e0e0e0;
                cursor: pointer;
                transition: all 0.2s;
            }
            .page-btn:hover {
                background: #3a3a3a;
                border-color: #4a9eff;
            }
            .page-btn.active {
                background: #4a9eff;
                border-color: #4a9eff;
            }
            .page-btn:disabled {
                opacity: 0.5;
                cursor: not-allowed;
            }
            .action-btn {
                padding: 4px 8px;
                margin: 0 2px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 12px;
                transition: all 0.2s;
            }
            .edit-btn {
                background: #4a9eff;
                color: white;
            }
            .edit-btn:hover {
                background: #3a8eef;
            }
            .delete-btn {
                background: #ff4444;
                color: white;
            }
            .delete-btn:hover {
                background: #ee3333;
            }
            .modal {
                display: none;
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.7);
                z-index: 1000;
                justify-content: center;
                align-items: center;
            }
            .modal.active {
                display: flex;
            }
            .modal-content {
                background: #2a2a2a;
                border: 1px solid #3a3a3a;
                border-radius: 8px;
                padding: 30px;
                max-width: 600px;
                width: 90%;
                max-height: 80vh;
                overflow-y: auto;
            }
            .modal-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }
            .modal-title {
                font-size: 20px;
                font-weight: 600;
                color: #fff;
            }
            .close-btn {
                background: none;
                border: none;
                color: #888;
                font-size: 24px;
                cursor: pointer;
                padding: 0;
                width: 30px;
                height: 30px;
            }
            .close-btn:hover {
                color: #fff;
            }
            .form-group {
                margin-bottom: 15px;
            }
            .form-label {
                display: block;
                margin-bottom: 5px;
                color: #e0e0e0;
                font-size: 14px;
            }
            .form-input {
                width: 100%;
                padding: 10px;
                background: #1a1a1a;
                border: 1px solid #3a3a3a;
                border-radius: 6px;
                color: #e0e0e0;
                font-size: 14px;
            }
            .form-input:focus {
                outline: none;
                border-color: #4a9eff;
            }
            .form-actions {
                display: flex;
                gap: 10px;
                justify-content: flex-end;
                margin-top: 20px;
            }
            .btn {
                padding: 10px 20px;
                border: none;
                border-radius: 6px;
                cursor: pointer;
                font-size: 14px;
                transition: background 0.2s;
            }
            .btn-primary {
                background: #4a9eff;
                color: white;
            }
            .btn-primary:hover {
                background: #3a8eef;
            }
            .btn-secondary {
                background: #3a3a3a;
                color: #e0e0e0;
            }
            .btn-secondary:hover {
                background: #4a4a4a;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>{{table_name}}</h1>
                <div style="display: flex; gap: 10px;">
                    <a href="/admin/" class="back-btn">← Back to Tables</a>
                    <button onclick="logout()" class="back-btn" style="background: #ff4444;">Logout</button>
                </div>
            </div>
            <div class="controls">
                <input type="text" id="searchInput" class="search-input" placeholder="Search...">
            </div>
            <div class="table-wrapper">
                <table id="dataTable">
                    <thead id="tableHead"></thead>
                    <tbody id="tableBody"></tbody>
                </table>
            </div>
            <div class="pagination" id="pagination"></div>
        </div>
        
        <!-- Edit Modal -->
        <div id="editModal" class="modal">
            <div class="modal-content">
                <div class="modal-header">
                    <h2 class="modal-title">Edit Record</h2>
                    <button class="close-btn" onclick="closeModal()">&times;</button>
                </div>
                <form id="editForm">
                    <div id="formFields"></div>
                    <div class="form-actions">
                        <button type="button" class="btn btn-secondary" onclick="closeModal()">Cancel</button>
                        <button type="submit" class="btn btn-primary">Save</button>
                    </div>
                </form>
            </div>
        </div>
        <script>
            const tableName = '{{ table_name }}';
            let allData = [];
            let currentPage = 1;
            const itemsPerPage = 50;
            
            function getPrimaryKey(row) {
                // Try common primary key names
                if (row.id !== undefined) return row.id;
                if (row.number !== undefined) return row.number;
                // Get first key as fallback
                return Object.keys(row)[0];
            }
            
            function getPrimaryKeyName(row) {
                if (row.id !== undefined) return 'id';
                if (row.number !== undefined) return 'number';
                return Object.keys(row)[0];
            }
            
            function renderTable(data) {
                if (data.length === 0) {
                    document.getElementById('tableBody').innerHTML = '<tr><td colspan="100%" class="empty">No data found</td></tr>';
                    return;
                }
                
                // Get headers from first row (exclude actions)
                const headers = Object.keys(data[0]);
                const thead = document.getElementById('tableHead');
                thead.innerHTML = '<tr>' + headers.map(h => `<th>${h}</th>`).join('') + '<th>Actions</th></tr>';
                
                // Render rows
                const tbody = document.getElementById('tableBody');
                tbody.innerHTML = data.map(row => {
                    const pkName = getPrimaryKeyName(row);
                    const pkValue = row[pkName];
                    const rowHtml = headers.map(h => {
                        let value = row[h];
                        if (value === null) value = '<em style="color: #888;">null</em>';
                        else if (typeof value === 'string' && value.length > 100) {
                            value = value.substring(0, 100) + '...';
                        }
                        return `<td>${value}</td>`;
                    }).join('');
                    return `<tr data-pk="${pkValue}" data-pk-name="${pkName}">${rowHtml}<td>
                        <button class="action-btn edit-btn" onclick="editRecord(${JSON.stringify(row).replace(/"/g, '&quot;')})">Edit</button>
                        <button class="action-btn delete-btn" onclick="deleteRecord('${pkName}', '${pkValue}')">Delete</button>
                    </td></tr>`;
                }).join('');
            }
            
            function editRecord(row) {
                const modal = document.getElementById('editModal');
                const formFields = document.getElementById('formFields');
                const pkName = getPrimaryKeyName(row);
                const pkValue = row[pkName];
                
                // Build form fields
                let html = '';
                for (const [key, value] of Object.entries(row)) {
                    // Skip primary key and read-only fields
                    if (key === pkName || key === 'createdAt' || key === 'created_at') {
                        html += `<input type="hidden" name="${key}" value="${value || ''}">`;
                        continue;
                    }
                    
                    const label = key.charAt(0).toUpperCase() + key.slice(1).replace(/([A-Z])/g, ' $1');
                    const inputValue = value === null ? '' : String(value);
                    html += `
                        <div class="form-group">
                            <label class="form-label">${label}</label>
                            <input type="text" class="form-input" name="${key}" value="${inputValue.replace(/"/g, '&quot;')}">
                        </div>
                    `;
                }
                formFields.innerHTML = html;
                
                // Store primary key info
                document.getElementById('editForm').dataset.pkName = pkName;
                document.getElementById('editForm').dataset.pkValue = pkValue;
                
                modal.classList.add('active');
            }
            
            function closeModal() {
                document.getElementById('editModal').classList.remove('active');
            }
            
            function deleteRecord(pkName, pkValue) {
                if (!confirm(`Are you sure you want to delete this record?`)) {
                    return;
                }
                
                fetch(`/admin/api/table/${tableName}/${pkValue}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    }
                })
                .then(async r => {
                    if (r.status === 401) {
                        localStorage.removeItem('admin_token');
                        window.location.href = '/admin/login';
                        return null;
                    }
                    return r.json();
                })
                .then(data => {
                    if (!data) return;
                    if (data.error) {
                        alert('Error: ' + data.error);
                        return;
                    }
                    alert('Record deleted successfully!');
                    loadData();
                })
                .catch(err => {
                    alert('Error: ' + err.message);
                });
            }
            
            document.getElementById('editForm').addEventListener('submit', (e) => {
                e.preventDefault();
                const form = e.target;
                const pkName = form.dataset.pkName;
                const pkValue = form.dataset.pkValue;
                
                const formData = new FormData(form);
                const data = {};
                for (const [key, value] of formData.entries()) {
                    data[key] = value;
                }
                
                fetch(`/admin/api/table/${tableName}/${pkValue}`, {
                    method: 'PUT',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(data)
                })
                .then(async r => {
                    if (r.status === 401) {
                        localStorage.removeItem('admin_token');
                        window.location.href = '/admin/login';
                        return null;
                    }
                    return r.json();
                })
                .then(data => {
                    if (!data) return;
                    if (data.error) {
                        alert('Error: ' + data.error);
                        return;
                    }
                    alert('Record updated successfully!');
                    closeModal();
                    loadData();
                })
                .catch(err => {
                    alert('Error: ' + err.message);
                });
            });
            
            function renderPagination(total) {
                const totalPages = Math.ceil(total / itemsPerPage);
                const pagination = document.getElementById('pagination');
                if (totalPages <= 1) {
                    pagination.innerHTML = '';
                    return;
                }
                
                let html = '';
                html += `<button class="page-btn" ${currentPage === 1 ? 'disabled' : ''} onclick="goToPage(${currentPage - 1})">Previous</button>`;
                for (let i = 1; i <= totalPages; i++) {
                    if (i === 1 || i === totalPages || (i >= currentPage - 2 && i <= currentPage + 2)) {
                        html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
                    } else if (i === currentPage - 3 || i === currentPage + 3) {
                        html += `<span style="padding: 8px; color: #888;">...</span>`;
                    }
                }
                html += `<button class="page-btn" ${currentPage === totalPages ? 'disabled' : ''} onclick="goToPage(${currentPage + 1})">Next</button>`;
                pagination.innerHTML = html;
            }
            
            function goToPage(page) {
                currentPage = page;
                loadData();
            }
            
            const token = localStorage.getItem('admin_token');
            if (!token) {
                window.location.href = '/admin/login';
            }
            
            function loadData() {
                fetch(`/admin/api/table/${tableName}?page=${currentPage}&limit=${itemsPerPage}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`
                    }
                })
                    .then(async r => {
                        if (r.status === 401) {
                            localStorage.removeItem('admin_token');
                            window.location.href = '/admin/login';
                            return null;
                        }
                        if (!r.ok) {
                            const errorData = await r.json().catch(() => ({error: 'Unknown error'}));
                            throw new Error(errorData.error || `HTTP ${r.status}: ${r.statusText}`);
                        }
                        return r.json();
                    })
                    .then(data => {
                        if (!data) return;
                        if (data.error) {
                            throw new Error(data.error);
                        }
                        if (!data.data) {
                            throw new Error('Invalid response format');
                        }
                        allData = data.data;
                        renderTable(data.data);
                        renderPagination(data.total);
                    })
                    .catch(err => {
                        console.error('Error loading data:', err);
                        const errorMsg = err.message || 'Error loading data';
                        document.getElementById('tableBody').innerHTML = `<tr><td colspan="100%" class="empty" style="color: #ff4444;">${errorMsg}</td></tr>`;
                    });
            }
            
            document.getElementById('searchInput').addEventListener('input', (e) => {
                const search = e.target.value.toLowerCase();
                const filtered = allData.filter(row => {
                    return Object.values(row).some(val => 
                        val !== null && String(val).toLowerCase().includes(search)
                    );
                });
                renderTable(filtered);
            });
            
            function logout() {
                localStorage.removeItem('admin_token');
                window.location.href = '/admin/login';
            }
            
            loadData();
        </script>
    </body>
    </html>
    """
    return render_template_string(html_template, table_name=table_name)

@admin_bp.route('/api/table/<table_name>')
@require_owner
def get_table_data(table_name):
    """Get table data with pagination"""
    if table_name not in TABLE_MODELS:
        return jsonify({'error': 'Table not found'}), 404
    
    session = get_session()
    try:
        model = TABLE_MODELS[table_name]
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 50, type=int)
        offset = (page - 1) * limit
        
        # Get total count
        total = session.query(model).count()
        
        # Get paginated data with order_by (required for OFFSET/LIMIT)
        query = session.query(model)
        
        # Try to order by created_at if exists, otherwise by primary key
        if hasattr(model, 'created_at'):
            query = query.order_by(model.created_at.desc())
        elif hasattr(model, 'id'):
            query = query.order_by(model.id.desc())
        else:
            # Get primary key column
            mapper = inspect(model)
            pk_columns = [col for col in mapper.columns if col.primary_key]
            if pk_columns:
                query = query.order_by(pk_columns[0].desc())
        
        records = query.offset(offset).limit(limit).all()
        
        # Convert to dict
        data = []
        mapper = inspect(model)  # Get mapper once for efficiency
        for record in records:
            try:
                if hasattr(record, 'to_dict'):
                    row_dict = record.to_dict()
                    # Ensure all values are serializable
                    for key, value in row_dict.items():
                        row_dict[key] = serialize_value(value)
                    data.append(row_dict)
                else:
                    # Fallback: use inspect to get all columns
                    row_dict = {}
                    for column in mapper.columns:
                        try:
                            value = getattr(record, column.name, None)
                            row_dict[column.name] = serialize_value(value)
                        except Exception as e:
                            row_dict[column.name] = None
                    data.append(row_dict)
            except Exception as e:
                # If to_dict fails, use fallback method
                try:
                    row_dict = {}
                    for column in mapper.columns:
                        try:
                            value = getattr(record, column.name, None)
                            row_dict[column.name] = serialize_value(value)
                        except:
                            row_dict[column.name] = None
                    data.append(row_dict)
                except Exception as e2:
                    # Last resort: log error and skip this record
                    import traceback
                    print(f"Error serializing record: {e2}")
                    traceback.print_exc()
                    continue
        
        return jsonify({
            'data': data,
            'total': total,
            'page': page,
            'limit': limit
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error loading data: {str(e)}'}), 500
    finally:
        session.close()

def get_primary_key(model):
    """Get primary key column name(s) for a model"""
    mapper = inspect(model)
    pk_columns = [col.name for col in mapper.columns if col.primary_key]
    return pk_columns[0] if pk_columns else None

def get_record_by_pk(session, model, pk_value):
    """Get record by primary key"""
    pk_name = get_primary_key(model)
    if not pk_name:
        return None
    return session.query(model).filter(getattr(model, pk_name) == pk_value).first()

@admin_bp.route('/api/table/<table_name>/<pk_value>', methods=['PUT'])
@require_owner
def update_table_record(table_name, pk_value):
    """Update a record in table"""
    if table_name not in TABLE_MODELS:
        return jsonify({'error': 'Table not found'}), 404
    
    session = get_session()
    try:
        model = TABLE_MODELS[table_name]
        record = get_record_by_pk(session, model, pk_value)
        
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        data = request.json
        if not data:
            return jsonify({'error': 'No data provided'}), 400
        
        # Update fields (skip primary key and read-only fields)
        mapper = inspect(model)
        pk_name = get_primary_key(model)
        read_only_fields = {'created_at', 'createdAt'}  # Don't update these
        
        for key, value in data.items():
            # Convert camelCase to snake_case if needed
            field_name = key
            # Try camelCase first, then snake_case
            if not hasattr(model, field_name):
                # Convert camelCase to snake_case (simple)
                field_name = ''.join('_' + c.lower() if c.isupper() else c for c in key).lstrip('_')
            
            if hasattr(model, field_name):
                # Skip primary key and read-only fields
                if field_name == pk_name or field_name in read_only_fields:
                    continue
                
                # Set the value
                try:
                    setattr(record, field_name, value)
                except Exception as e:
                    return jsonify({'error': f'Error updating field {field_name}: {str(e)}'}), 400
        
        session.commit()
        session.refresh(record)
        
        # Return updated record
        if hasattr(record, 'to_dict'):
            result = record.to_dict()
            for key, value in result.items():
                result[key] = serialize_value(value)
        else:
            mapper = inspect(model)
            result = {}
            for column in mapper.columns:
                value = getattr(record, column.name, None)
                result[column.name] = serialize_value(value)
        
        return jsonify({'data': result, 'message': 'Record updated successfully'}), 200
        
    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error updating record: {str(e)}'}), 500
    finally:
        session.close()

@admin_bp.route('/api/table/<table_name>/<pk_value>', methods=['DELETE'])
@require_owner
def delete_table_record(table_name, pk_value):
    """Delete a record from table"""
    if table_name not in TABLE_MODELS:
        return jsonify({'error': 'Table not found'}), 404
    
    session = get_session()
    try:
        model = TABLE_MODELS[table_name]
        record = get_record_by_pk(session, model, pk_value)
        
        if not record:
            return jsonify({'error': 'Record not found'}), 404
        
        session.delete(record)
        session.commit()
        
        return jsonify({'message': 'Record deleted successfully'}), 200
        
    except Exception as e:
        session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({'error': f'Error deleting record: {str(e)}'}), 500
    finally:
        session.close()

