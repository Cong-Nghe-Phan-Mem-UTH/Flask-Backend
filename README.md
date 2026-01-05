# Flask Backend - Clean Architecture

Backend API được xây dựng với Flask theo Clean Architecture pattern.

## 📁 Cấu trúc thư mục

```
Flask-BackEnd/
├── src/
│   ├── api/              # API layer (routes, middleware)
│   │   ├── auth/
│   │   └── routes/
│   ├── domain/           # Domain layer (business logic models, constants, exceptions)
│   │   ├── constants.py
│   │   └── exceptions.py
│   ├── infrastructure/   # Infrastructure layer (database, models)
│   │   ├── databases/
│   │   └── models/
│   ├── services/         # Services layer (business logic)
│   ├── utils/            # Utilities (JWT, crypto, helpers, socket)
│   ├── plugins/          # Plugins (Socket.IO)
│   ├── jobs/             # Background jobs
│   ├── config.py
│   ├── create_app.py
│   ├── app.py
│   └── error_handler.py
├── migrations/
├── requirements.txt
└── README.md
```

## 🚀 Cài đặt

1. **Tạo môi trường ảo:**

```bash
cd /Users/mac/Documents/project_cnpm/Flask-BackEnd/src
python3 -m venv .venv
source .venv/bin/activate  # MacOS/Linux
# hoặc
.venv\Scripts\activate  # Windows
```

2. **Cài đặt dependencies:**

```bash
pip install -r requirements.txt
```

**Hoặc nếu bạn đang ở thư mục gốc của project:**

```bash
cd src
python3 -m venv .venv
source .venv/bin/activate  # MacOS/Linux
pip install -r requirements.txt
```

3. **Tạo file `.env` trong thư mục `src/`:**

**Với SQLite (mặc định):**

```env
DATABASE_URL=sqlite:///dev.db
ACCESS_TOKEN_SECRET=your-access-token-secret
REFRESH_TOKEN_SECRET=your-refresh-token-secret
INITIAL_EMAIL_OWNER=admin@order.com
INITIAL_PASSWORD_OWNER=123456
PORT=4000
```

**Với MSSQL (Microsoft SQL Server):**

**Option 1: Sử dụng pyodbc (khuyến nghị)**

- Cần cài đặt ODBC Driver cho SQL Server trước
- Windows: Đã có sẵn hoặc tải từ Microsoft
- MacOS: `brew install msodbcsql17` hoặc `brew install msodbcsql18`
- Linux: Tải từ Microsoft hoặc dùng package manager

```env
DATABASE_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+17+for+SQL+Server
# Hoặc với ODBC Driver 18 (hỗ trợ encryption mặc định)
DATABASE_URL=mssql+pyodbc://username:password@server/database?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
```

**Option 2: Sử dụng pymssql (dễ cài hơn, pure Python)**

```env
DATABASE_URL=mssql+pymssql://username:password@server:1433/database
```

**Lưu ý:** Thay `username`, `password`, `server`, và `database` bằng thông tin thực tế của bạn.

4. **Chạy ứng dụng:**

**Chạy Backend riêng:**

```bash
cd src
python app.py
```

Server sẽ chạy tại `http://localhost:4000` với Socket.IO hỗ trợ real-time.

**Chạy cả Backend + Frontend cùng lúc:**

**MacOS/Linux:**

```bash
cd Flask-BackEnd
chmod +x scripts/start_dev.sh
./scripts/start_dev.sh
```

**Windows:**

**Option 1: Chạy trong cùng terminal (tương tự MacOS/Linux):**

```cmd
cd Flask-BackEnd
scripts\start_dev_same_terminal.bat
```

**Option 2: Sử dụng PowerShell:**

```powershell
cd Flask-BackEnd
powershell -ExecutionPolicy Bypass -File scripts\start_dev.ps1
```

**Option 3: Mở 2 cửa sổ riêng biệt (dễ theo dõi output):**

```cmd
cd Flask-BackEnd
scripts\start_dev.bat
```

**Hoặc sử dụng VS Code Tasks:**

1. Mở Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Chọn "Tasks: Run Task"
3. Chọn "Start All (Backend + Frontend)"

Xem thêm chi tiết trong [DEVELOPMENT.md](./DEVELOPMENT.md)

## 📡 API Endpoints

### Authentication

- `POST /auth/login` - Đăng nhập
- `POST /auth/logout` - Đăng xuất
- `POST /auth/refresh-token` - Refresh token
- `GET /auth/login/google` - Đăng nhập bằng Google OAuth

### Account

- `GET /accounts/` - Lấy danh sách tài khoản (Owner only)
- `POST /accounts/` - Tạo tài khoản nhân viên (Owner only)
- `GET /accounts/detail/<id>` - Lấy chi tiết tài khoản
- `PUT /accounts/detail/<id>` - Cập nhật tài khoản
- `DELETE /accounts/detail/<id>` - Xóa tài khoản
- `GET /accounts/me` - Lấy thông tin tài khoản hiện tại
- `PUT /accounts/me` - Cập nhật thông tin tài khoản hiện tại
- `PUT /accounts/change-password` - Đổi mật khẩu
- `PUT /accounts/change-password-v2` - Đổi mật khẩu (với token mới)

### Dish

- `GET /dishes/` - Lấy danh sách món ăn
- `GET /dishes/pagination` - Lấy danh sách món ăn có phân trang
- `GET /dishes/<id>` - Lấy chi tiết món ăn
- `POST /dishes/` - Tạo món ăn (Owner/Employee)
- `PUT /dishes/<id>` - Cập nhật món ăn (Owner/Employee)
- `DELETE /dishes/<id>` - Xóa món ăn (Owner/Employee)

### Table

- `GET /tables/` - Lấy danh sách bàn
- `GET /tables/<number>` - Lấy chi tiết bàn
- `POST /tables/` - Tạo bàn (Owner/Employee)
- `PUT /tables/<number>` - Cập nhật bàn (Owner/Employee)
- `DELETE /tables/<number>` - Xóa bàn (Owner/Employee)

### Order

- `POST /orders/` - Tạo đơn hàng (Owner/Employee)
- `GET /orders/` - Lấy danh sách đơn hàng (Owner/Employee)
- `GET /orders/<id>` - Lấy chi tiết đơn hàng (Owner/Employee)
- `PUT /orders/<id>` - Cập nhật đơn hàng (Owner/Employee)
- `POST /orders/pay` - Thanh toán đơn hàng (Owner/Employee)

### Guest

- `POST /guest/auth/login` - Đăng nhập khách
- `POST /guest/auth/logout` - Đăng xuất khách
- `POST /guest/auth/refresh-token` - Refresh token khách
- `POST /guest/orders` - Tạo đơn hàng (Guest)
- `GET /guest/orders` - Lấy danh sách đơn hàng (Guest)

### Media

- `POST /media/upload` - Upload ảnh (Owner/Employee)

**Cách sử dụng:**

1. **Từ Frontend (JavaScript/React):**

```javascript
// Tạo FormData với file
const formData = new FormData();
formData.append("file", fileInput.files[0]); // hoặc 'image', 'avatar'

// Gửi request
const response = await fetch("http://localhost:4000/media/upload", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${accessToken}`,
    // KHÔNG set Content-Type header, browser sẽ tự động set multipart/form-data
  },
  body: formData,
});

const result = await response.json();
console.log(result.data); // URL của ảnh: http://localhost:4000/static/filename.jpg
```

**Ví dụ với React:**

```jsx
const handleImageUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const response = await fetch("http://localhost:4000/media/upload", {
      method: "POST",
      headers: {
        Authorization: `Bearer ${accessToken}`,
      },
      body: formData,
    });

    const result = await response.json();
    if (response.ok) {
      // Sử dụng URL ảnh
      const imageUrl = result.data;
      console.log("Upload thành công:", imageUrl);
      // Có thể dùng imageUrl để cập nhật avatar hoặc ảnh món ăn
    }
  } catch (error) {
    console.error("Lỗi upload:", error);
  }
};

// Trong component
<input type="file" accept="image/*" onChange={handleImageUpload} />;
```

2. **Test bằng cURL:**

```bash
curl -X POST http://localhost:4000/media/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/image.jpg"
```

3. **Test bằng Postman:**
   - Method: `POST`
   - URL: `http://localhost:4000/media/upload`
   - Headers: `Authorization: Bearer YOUR_ACCESS_TOKEN`
   - Body: chọn `form-data`
   - Key: `file` (type: File)
   - Value: chọn file ảnh

**Response:**

```json
{
  "message": "Upload ảnh thành công",
  "data": "http://localhost:4000/static/abc123def456.jpg"
}
```

**Lưu ý:**

- File field name có thể là: `file`, `image`, hoặc `avatar`
- Định dạng hỗ trợ: png, jpg, jpeg, gif, webp
- Giới hạn kích thước: 10MB
- Cần đăng nhập với quyền Owner hoặc Employee

### Static

- `GET /static/<filename>` - Lấy file tĩnh

### Indicator

- `GET /indicators/dashboard` - Lấy dashboard statistics (Owner/Employee)

### Test

- `GET /test/` - Test API

## 🔌 Socket.IO

Server hỗ trợ Socket.IO cho real-time communication:

**Events được emit:**

- `new-order` - Khi có đơn hàng mới
- `update-order` - Khi cập nhật đơn hàng
- `payment` - Khi thanh toán
- `new-dish` - Khi có món ăn mới (data: dish object)
- `update-dish` - Khi cập nhật món ăn (data: dish object)
- `delete-dish` - Khi xóa món ăn (data: {id: dish_id})
- `refresh-token` - Khi refresh token (khi đổi role)
- `logout` - Khi logout

**Cách kết nối:**

```javascript
import io from "socket.io-client";

const socket = io("http://localhost:4000", {
  auth: {
    Authorization: `Bearer ${accessToken}`,
  },
});

socket.on("new-order", (data) => {
  console.log("New order:", data);
});
```

## 📝 Ghi chú

- Code được tổ chức theo Clean Architecture pattern
- Sử dụng SQLAlchemy ORM
- JWT authentication với access token và refresh token
- Bcrypt cho password hashing
- Socket.IO cho real-time features
- Background jobs tự động chạy (xóa refresh tokens hết hạn)
- Error handling tập trung

## 🌐 Frontend Integration

Project này được tích hợp với Next.js Frontend (`NextJs-Super-FrontEnd`).

### Cấu trúc Project

```
project_cnpm/
├── Flask-BackEnd/          # Flask Backend API (port 4000)
└── NextJs-Super-FrontEnd/  # Next.js Frontend (port 3000)
```

### Chạy Development Servers

Xem chi tiết trong [DEVELOPMENT.md](./DEVELOPMENT.md) để biết cách:

- Chạy cả Backend và Frontend cùng lúc
- Sử dụng VS Code Tasks
- Troubleshooting các vấn đề thường gặp

### Configuration

**Backend CORS:** Đã được cấu hình để cho phép frontend kết nối:

```python
CORS(app, origins='*', supports_credentials=True)
```

**Frontend API URL:** Đảm bảo frontend config trỏ đến `http://localhost:4000`
chayj be va fe cung luc : cd /Users/mac/Documents/project_cnpm/Flask-BackEnd
./scripts/start_dev.sh
