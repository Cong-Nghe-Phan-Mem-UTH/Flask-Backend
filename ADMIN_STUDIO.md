# Database Studio - Prisma Studio Style

Công cụ quản lý database tương tự Prisma Studio, chạy ở port 5555.

## 🚀 Cài đặt

1. **Cài đặt dependencies:**
```bash
cd src
pip install -r requirements.txt
```

2. **Chạy Database Studio:**
```bash
cd src
python admin_studio.py
```

Database Studio sẽ chạy tại: **http://localhost:5555**

## 📊 Sử dụng

1. **Truy cập:** http://localhost:5555
2. **Đăng nhập:** Sử dụng tài khoản Owner
   - Email: `admin@order.com` (hoặc email Owner của bạn)
   - Password: `123456` (hoặc password Owner của bạn)

3. **Quản lý database:**
   - Xem tất cả các bảng trong sidebar
   - Click vào bảng để xem dữ liệu
   - Thêm, sửa, xóa records trực tiếp từ UI
   - Tìm kiếm và filter dữ liệu

## 🎯 Tính năng

- ✅ UI đẹp, tương tự Prisma Studio
- ✅ Quản lý tất cả models: Account, Dish, Table, Order, Guest, etc.
- ✅ CRUD operations (Create, Read, Update, Delete)
- ✅ Authentication với Owner role
- ✅ Chạy độc lập ở port 5555
- ✅ Hỗ trợ tìm kiếm và filter

## 🔧 Cấu hình

Có thể thay đổi port bằng biến môi trường:
```bash
ADMIN_PORT=5555 python admin_studio.py
```

## 📝 Lưu ý

- Chỉ Owner mới có quyền truy cập Database Studio
- Database Studio sử dụng cùng database với app chính
- Đảm bảo app chính đang chạy hoặc database đã được khởi tạo

## 🆚 So sánh với Prisma Studio

| Tính năng | Prisma Studio | Database Studio |
|-----------|--------------|-----------------|
| Port | 5555 | 5555 ✅ |
| UI | Modern | Bootstrap 4 ✅ |
| CRUD | ✅ | ✅ |
| Search/Filter | ✅ | ✅ |
| Authentication | ❌ | ✅ (Owner only) |
| Multiple DBs | ✅ | ✅ (SQLite/MSSQL/PostgreSQL/MySQL) |


