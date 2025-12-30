# Ghi chú về chuyển đổi từ Node.js sang Flask

## Đã chuyển đổi hoàn toàn

### ✅ Routes
- ✅ `/auth/*` - Authentication routes
- ✅ `/accounts/*` - Account management
- ✅ `/dishes/*` - Dish management
- ✅ `/tables/*` - Table management
- ✅ `/orders/*` - Order management
- ✅ `/guest/*` - Guest routes
- ✅ `/media/*` - Media upload
- ✅ `/static/*` - Static files
- ✅ `/test/*` - Test route
- ✅ `/indicators/*` - Dashboard indicators

### ✅ Services (Business Logic)
- ✅ Auth service (login, logout, refresh token, Google OAuth)
- ✅ Account service (CRUD, me, change password)
- ✅ Dish service (CRUD với pagination)
- ✅ Table service (CRUD)
- ✅ Order service (CRUD, pay)
- ✅ Guest service (login, logout, orders)
- ✅ Media service (upload image)
- ✅ Indicator service (dashboard statistics)

### ✅ Models
- ✅ AccountModel
- ✅ DishModel, DishSnapshotModel
- ✅ TableModel
- ✅ OrderModel
- ✅ GuestModel
- ✅ RefreshTokenModel
- ✅ SocketModel

### ✅ Middleware & Authentication
- ✅ require_logined
- ✅ require_owner
- ✅ require_employee
- ✅ require_guest
- ✅ require_owner_or_employee
- ✅ pause_api_check

### ✅ Utils
- ✅ JWT utils (sign/verify tokens)
- ✅ Crypto utils (hash/compare password)
- ✅ Helpers (random_id, create_folder)

### ✅ Background Jobs
- ✅ Auto remove expired refresh tokens (chạy mỗi giờ)

### ✅ Error Handling
- ✅ EntityError, AuthError, StatusError, ForbiddenError
- ✅ Centralized error handler

## ✅ Đã thêm Socket.IO hoàn chỉnh

### Socket.IO
**Đã tích hợp hoàn toàn:**
- ✅ Socket.IO connection với authentication
- ✅ Emit events khi có order mới (`new-order`)
- ✅ Emit events khi update order (`update-order`)
- ✅ Emit events khi payment (`payment`)
- ✅ Emit events khi refresh token (`refresh-token`)
- ✅ Emit events khi logout (`logout`)
- ✅ Manager room cho Owner/Employee
- ✅ Socket tracking cho Guest và Account
- ✅ Auto join manager room cho Owner/Employee

**Cách sử dụng:**
- Server tự động khởi động với Socket.IO
- Client cần kết nối với Socket.IO và gửi Authorization trong handshake
- Events được emit tự động khi có thay đổi

### Validation Schemas
**Node.js gốc:** Sử dụng Zod cho validation
**Flask:** 
- Validation được xử lý trong services
- Có thể thêm Marshmallow hoặc Pydantic nếu cần validation mạnh hơn

## Cách sử dụng

1. Cài đặt dependencies:
```bash
cd flask_backend/src
pip install -r requirements.txt
```

2. Tạo file `.env` với các biến môi trường

3. Chạy:
```bash
python app.py
```

## Lưu ý

- Database sẽ tự động tạo tables khi chạy lần đầu
- Tài khoản Owner sẽ tự động được tạo nếu chưa có
- Background job sẽ tự động chạy để xóa refresh tokens hết hạn
- Socket.IO đã được tích hợp hoàn chỉnh với real-time features
- Server chạy với eventlet để hỗ trợ Socket.IO

