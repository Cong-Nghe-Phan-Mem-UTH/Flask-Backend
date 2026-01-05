# Hướng dẫn Migrate Dữ liệu từ Node.js Backend sang Flask Backend

Script này sẽ copy toàn bộ dữ liệu từ database SQLite của Node.js backend sang MSSQL database của Flask backend.

## 📋 Yêu cầu

1. Node.js backend database phải tồn tại tại: `NextJs-Super-BackEnd/prisma/dev.db`
2. Flask backend đã được cấu hình và kết nối với MSSQL database
3. File `.env` trong `Flask-BackEnd/src/` đã được cấu hình đúng

## 🚀 Cách chạy

```bash
cd /Users/mac/Documents/project_cnpm/Flask-BackEnd
python3 scripts/migrate_data.py
```

Hoặc:

```bash
cd Flask-BackEnd/src
source .venv/bin/activate
cd ..
python3 scripts/migrate_data.py
```

## 📦 Dữ liệu sẽ được migrate

1. **Accounts** - Tài khoản (Owner, Employee)
2. **Dishes** - Món ăn
3. **Dish Snapshots** - Ảnh chụp món ăn
4. **Tables** - Bàn ăn
5. **Guests** - Khách hàng
6. **Orders** - Đơn hàng
7. **Upload Files** - Tất cả file ảnh từ thư mục `uploads/`

## ⚠️ Lưu ý

- Script sẽ **bỏ qua** các bản ghi đã tồn tại (dựa trên email cho Account, name cho Dish, number cho Table)
- Foreign keys sẽ được tự động map lại (ID mới sẽ được tạo trong MSSQL)
- Nếu chạy lại script, nó sẽ chỉ thêm dữ liệu mới, không duplicate

## 🔍 Kiểm tra sau khi migrate

1. Kiểm tra số lượng records:
   ```sql
   SELECT COUNT(*) FROM Account;
   SELECT COUNT(*) FROM Dish;
   SELECT COUNT(*) FROM [Order];
   ```

2. Kiểm tra trang chủ frontend - dishes sẽ hiển thị đầy đủ

3. Kiểm tra uploads folder có đầy đủ file ảnh không

## 🐛 Troubleshooting

**Lỗi: "SQLite database not found"**
- Kiểm tra đường dẫn: `NextJs-Super-BackEnd/prisma/dev.db`
- Đảm bảo Node.js backend đã chạy ít nhất 1 lần để tạo database

**Lỗi: "Cannot connect to MSSQL"**
- Kiểm tra file `.env` có đúng connection string không
- Kiểm tra SQL Server đang chạy
- Kiểm tra database `FlaskApiDB` đã tồn tại chưa

**Lỗi: "Foreign key constraint"**
- Script đã xử lý mapping IDs tự động
- Nếu vẫn lỗi, có thể do dữ liệu không hợp lệ trong SQLite


