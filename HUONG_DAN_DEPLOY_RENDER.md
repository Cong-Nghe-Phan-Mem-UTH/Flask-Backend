# 🚀 Hướng dẫn Deploy Flask Backend lên Render (FREE)

Hướng dẫn chi tiết từng bước để deploy Flask Backend lên Render hoàn toàn miễn phí.

---

## 📋 Yêu cầu

1. ✅ Tài khoản GitHub (code đã push lên GitHub)
2. ✅ Tài khoản Render (đăng ký miễn phí tại [render.com](https://render.com))

---

## 🗄️ BƯỚC 1: Tạo PostgreSQL Database (Làm trước)

### 1.1. Tạo Database

1. Đăng nhập [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"PostgreSQL"**
3. Điền thông tin:
   - **Name**: `flask-db`
   - **Database**: `flaskdb`
   - **User**: Để trống (tự động tạo)
   - **Region**: `Singapore (Southeast Asia)` ⚠️ **QUAN TRỌNG: Chọn Singapore**
   - **PostgreSQL Version**: `18` (hoặc mặc định)
   - **Instance Type**: Chọn **`Free`**
4. Click **"Create Database"**
5. Đợi vài phút để Render tạo database

### 1.2. Copy Database URL

1. Sau khi database tạo xong, click vào database `flask-db`
2. Vào tab **"Connections"**
3. Tìm **"Internal Database URL"**
4. Click icon **Copy** để copy toàn bộ URL
5. **Lưu lại URL này** để dùng ở bước sau

**Ví dụ URL:**
```
postgresql://flaskdb_cqbr_user:EDofnA3Lh6EQc867N19Tjus0QwbECQZ1@dpg-d5fj2ingi27c73ds0gi0-a/flaskdb_cqbr
```

⚠️ **Lưu ý:** URL phải có dấu `@` giữa password và hostname!

---

## 🌐 BƯỚC 2: Tạo Web Service

### 2.1. Tạo Web Service mới

1. Trong Render Dashboard, click **"New +"** → **"Web Service"**
2. Connect GitHub repository của bạn
3. Chọn repository `Flask-BackEnd` (hoặc tên repo của bạn)

### 2.2. Cấu hình Basic Settings

Điền các thông tin sau:

| Trường | Giá trị |
|--------|---------|
| **Name** | `flask-backend` (hoặc tên bạn muốn) |
| **Language** | `Python 3` |
| **Branch** | `main` (hoặc `master`) |
| **Region** | `Singapore (Southeast Asia)` ⚠️ **Phải cùng region với Database** |
| **Root Directory** | Để **TRỐNG** |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `cd src && python app.py` |

⚠️ **Lưu ý:** 
- Dấu `$` ở đầu Build Command là tự động, không cần xóa
- Root Directory phải để trống vì `requirements.txt` ở root

### 2.3. Chọn Instance Type

- Scroll xuống phần **"Instance Type"**
- Chọn **`Free`** (miễn phí)

---

## 🔐 BƯỚC 3: Cấu hình Environment Variables

Trong phần **"Environment Variables"**, click **"+ Add Environment Variable"** và thêm từng biến sau:

### 3.1. Database

```
NAME: DATABASE_URL
VALUE: [Paste URL đã copy từ Bước 1.2]
```

**Ví dụ:**
```
postgresql://flaskdb_cqbr_user:EDofnA3Lh6EQc867N19Tjus0QwbECQZ1@dpg-d5fj2ingi27c73ds0gi0-a/flaskdb_cqbr
```

### 3.2. JWT Secrets (Click nút "Generate" để tự động tạo)

```
NAME: SECRET_KEY
VALUE: [Click "Generate" để tạo tự động]
```

```
NAME: ACCESS_TOKEN_SECRET
VALUE: [Click "Generate" để tạo tự động]
```

```
NAME: REFRESH_TOKEN_SECRET
VALUE: [Click "Generate" để tạo tự động]
```

### 3.3. Server Config

```
NAME: PORT
VALUE: 4000
```

```
NAME: PROTOCOL
VALUE: https
```

```
NAME: PRODUCTION
VALUE: true
```

```
NAME: DEBUG
VALUE: false
```

```
NAME: SERVER_TIMEZONE
VALUE: Asia/Ho_Chi_Minh
```

```
NAME: PAUSE_SOME_ENDPOINTS
VALUE: false
```

### 3.4. Initial Owner Account

```
NAME: INITIAL_EMAIL_OWNER
VALUE: admin@order.com
```

```
NAME: INITIAL_PASSWORD_OWNER
VALUE: 123456
```

### 3.5. Upload Folder

```
NAME: UPLOAD_FOLDER
VALUE: uploads
```

### 3.6. Các biến tùy chọn (Có thể thêm sau khi deploy)

```
NAME: PRODUCTION_URL
VALUE: https://flask-backend.onrender.com
```
⚠️ Thay `flask-backend` bằng tên Web Service của bạn

```
NAME: CLIENT_URL
VALUE: https://your-frontend-url.vercel.app
```
⚠️ Thay bằng URL frontend của bạn (nếu có)

---

## 🚀 BƯỚC 4: Deploy

1. Scroll xuống cuối trang
2. Click nút **"Deploy Web Service"** (màu đen)
3. Đợi vài phút để Render:
   - Clone code từ GitHub
   - Install dependencies từ `requirements.txt`
   - Start application
4. Xem **Logs** để kiểm tra quá trình deploy

### 4.1. Kiểm tra Deploy thành công

- Khi deploy xong, bạn sẽ thấy status **"Live"**
- URL của app: `https://flask-backend.onrender.com` (thay `flask-backend` bằng tên của bạn)
- Test API: Mở URL trên trình duyệt hoặc dùng Postman

---

## ✅ Checklist trước khi Deploy

- [ ] Database đã tạo xong và đã copy Internal Database URL
- [ ] Database và Web Service cùng region (Singapore)
- [ ] Build Command: `pip install -r requirements.txt`
- [ ] Start Command: `cd src && python app.py`
- [ ] Root Directory: Để trống
- [ ] Instance Type: Free
- [ ] DATABASE_URL đã điền đúng (có dấu `@`)
- [ ] SECRET_KEY, ACCESS_TOKEN_SECRET, REFRESH_TOKEN_SECRET đã generate
- [ ] DEBUG = false
- [ ] PRODUCTION = true
- [ ] PROTOCOL = https

---

## 🐛 Xử lý lỗi thường gặp

### ❌ Lỗi: Database connection failed

**Nguyên nhân:**
- DATABASE_URL sai format (thiếu dấu `@`)
- Database và Web Service khác region
- Database chưa được tạo

**Cách sửa:**
1. Kiểm tra DATABASE_URL có đúng format không
2. Đảm bảo Database và Web Service cùng region (Singapore)
3. Kiểm tra database đã được tạo và đang chạy

### ❌ Lỗi: Port already in use

**Nguyên nhân:**
- Code không lấy PORT từ environment variable

**Cách sửa:**
- Đảm bảo `src/app.py` có dòng:
```python
port = int(os.environ.get('PORT', 4000))
```

### ❌ Lỗi: Module not found

**Nguyên nhân:**
- Thiếu package trong `requirements.txt`

**Cách sửa:**
- Kiểm tra `requirements.txt` có đầy đủ packages không
- Xem Logs để biết package nào thiếu

**Lỗi thường gặp:**
- `ModuleNotFoundError: No module named 'psycopg2'` → Thêm `psycopg2-binary>=2.9` vào `requirements.txt`
- `ModuleNotFoundError: No module named 'eventlet'` → Đảm bảo có `eventlet>=0.33` trong `requirements.txt`

### ❌ Lỗi: Deployment Timed Out

**Nguyên nhân:**
- App không start được trong thời gian quy định (thường 15-20 phút)
- Database connection timeout khi tạo tables
- App đang chờ một service nào đó

**Cách sửa:**
1. **Kiểm tra Logs**: Xem logs chi tiết để tìm lỗi cụ thể
2. **Kiểm tra Database URL**: Đảm bảo DATABASE_URL đúng format và database đã được tạo
3. **Kiểm tra Start Command**: Đảm bảo là `cd src && python app.py`
4. **Thử lại**: Click "Manual Deploy" để deploy lại
5. **Nếu vẫn lỗi**: Kiểm tra xem có lỗi trong code không (xem logs)

### ❌ App sleep quá lâu

**Nguyên nhân:**
- Free tier sẽ sleep sau 15 phút không có traffic

**Cách sửa:**
- Lần đầu wake up có thể mất 30-60 giây
- Có thể dùng [UptimeRobot](https://uptimerobot.com) (free) để ping app mỗi 5 phút

---

## 📝 Lưu ý quan trọng

### ⚠️ Free Tier Limitations

- **Sleep sau 15 phút**: Nếu không có traffic 15 phút, app sẽ sleep
- **Lần đầu wake up**: Có thể mất 30-60 giây
- **Persistent storage**: Files uploads sẽ được lưu, nhưng nên backup định kỳ

### ✅ Những gì hoạt động tốt

- ✅ Flask API
- ✅ Socket.IO (WebSocket)
- ✅ Background Jobs (APScheduler)
- ✅ File Uploads (local storage)
- ✅ PostgreSQL Database

---

## 🎯 Sau khi Deploy thành công

1. **Test API**: Mở URL app trên trình duyệt
2. **Kiểm tra Logs**: Vào Web Service → Logs để xem logs real-time
3. **Update PRODUCTION_URL**: Thêm environment variable `PRODUCTION_URL` với URL của app
4. **Cập nhật CLIENT_URL**: Thêm URL frontend của bạn (nếu có)

---

## 📚 Tài liệu tham khảo

- [Render Documentation](https://render.com/docs)
- [Deploy Python on Render](https://render.com/docs/deploy-python)
- [Render PostgreSQL](https://render.com/docs/databases)

---

## 💡 Tips

- **Auto-Deploy**: Render tự động deploy khi bạn push code lên GitHub (nếu bật)
- **Logs**: Luôn kiểm tra Logs khi có lỗi
- **Backup**: Nên backup database và files định kỳ
- **Monitoring**: Có thể dùng UptimeRobot để monitor app free

---

**Chúc bạn deploy thành công! 🎉**

