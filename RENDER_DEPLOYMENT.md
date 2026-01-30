# 🎨 Hướng dẫn Deploy Flask Backend lên Render (FREE TIER)

## ✅ Tại sao chọn Render cho project học tập?

- ✅ **HOÀN TOÀN MIỄN PHÍ** (free tier)
- ✅ Hỗ trợ đầy đủ Flask, Socket.IO, Background Jobs
- ✅ Deploy dễ dàng từ GitHub
- ✅ Database PostgreSQL miễn phí
- ⚠️ Sleep sau 15 phút không có traffic (OK cho demo)

## 📋 Yêu cầu

1. Tài khoản GitHub (để deploy)
2. Tài khoản Render (đăng ký miễn phí tại [render.com](https://render.com))

## 🚀 Các bước deploy

### Bước 1: Chuẩn bị code trên GitHub

1. Push code lên GitHub repository (nếu chưa có)
2. Đảm bảo có file `requirements.txt` ở root hoặc `src/`

### Bước 2: Tạo Web Service trên Render

1. Đăng nhập vào [Render Dashboard](https://dashboard.render.com)
2. Click **"New +"** → **"Web Service"**
3. Connect GitHub repository của bạn
4. Chọn repository `Flask-BackEnd`

### Bước 3: Cấu hình Web Service

**Basic Settings:**
- **Name**: `flask-backend` (hoặc tên bạn muốn)
- **Region**: Chọn gần nhất (Singapore, US, etc.)
- **Branch**: `main` hoặc `master`
- **Root Directory**: Để trống (hoặc `src` nếu cấu trúc khác)
- **Runtime**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt
  ```
- **Start Command**: 
  ```bash
  cd src && python app.py
  ```
  Hoặc nếu `requirements.txt` ở root:
  ```bash
  pip install -r requirements.txt && cd src && python app.py
  ```

**Advanced Settings:**
- **Instance Type**: `Free` (miễn phí)
- **Auto-Deploy**: `Yes` (tự động deploy khi push code)

### Bước 4: Cấu hình Environment Variables

Trong phần **Environment Variables**, thêm các biến sau:

```env
# Database (sẽ tạo ở bước tiếp theo)
DATABASE_URL=postgresql://... (sẽ có sau khi tạo database)

# JWT Secrets
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_SECRET=your-access-token-secret
REFRESH_TOKEN_SECRET=your-refresh-token-secret

# Server Config
PORT=4000
DOMAIN=your-app-name.onrender.com
PROTOCOL=https
PRODUCTION=true
PRODUCTION_URL=https://your-app-name.onrender.com

# Client URL (URL frontend của bạn)
CLIENT_URL=https://your-frontend-url.vercel.app

# Initial Owner Account
INITIAL_EMAIL_OWNER=admin@order.com
INITIAL_PASSWORD_OWNER=123456

# Upload Folder (sẽ dùng local trên Render)
UPLOAD_FOLDER=uploads

# Other
SERVER_TIMEZONE=Asia/Ho_Chi_Minh
PAUSE_SOME_ENDPOINTS=false
```

### Bước 5: Tạo PostgreSQL Database (FREE)

1. Trong Render Dashboard, click **"New +"** → **"PostgreSQL"**
2. **Name**: `flask-db` (hoặc tên bạn muốn)
3. **Database**: `flaskdb` (hoặc tên bạn muốn)
4. **User**: Tự động tạo
5. **Region**: Cùng region với Web Service
6. **Plan**: `Free`
7. Click **"Create Database"**

Sau khi tạo xong:
1. Vào database → **"Connections"** → Copy **"Internal Database URL"**
2. Quay lại Web Service → **Environment Variables**
3. Thêm/update `DATABASE_URL` với URL vừa copy

**Format URL sẽ như:**
```
postgresql://user:password@dpg-xxxxx-a.singapore-postgres.render.com/flaskdb
```

### Bước 6: Deploy

1. Click **"Create Web Service"**
2. Render sẽ tự động:
   - Clone code từ GitHub
   - Install dependencies
   - Start application
3. Đợi vài phút để build và deploy
4. Khi xong, bạn sẽ có URL: `https://your-app-name.onrender.com`

## 🔧 Cấu hình bổ sung

### File `render.yaml` (Optional - để tự động hóa)

Tạo file `render.yaml` ở root của project:

```yaml
services:
  - type: web
    name: flask-backend
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: cd src && python app.py
    envVars:
      - key: DATABASE_URL
        fromDatabase:
          name: flask-db
          property: connectionString
      - key: SECRET_KEY
        generateValue: true
      - key: ACCESS_TOKEN_SECRET
        generateValue: true
      - key: REFRESH_TOKEN_SECRET
        generateValue: true
      - key: PORT
        value: 4000
      - key: PRODUCTION
        value: true
      - key: PROTOCOL
        value: https

databases:
  - name: flask-db
    databaseName: flaskdb
    user: flaskuser
    plan: free
```

### Cập nhật `app.py` để chạy trên Render

File `src/app.py` hiện tại:
```python
if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=4000, debug=True)
```

Cần cập nhật để lấy port từ environment:
```python
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 4000))
    socketio.run(app, host="0.0.0.0", port=port, debug=False)
```

## ⚠️ Lưu ý quan trọng

### 1. Free Tier Limitations

- **Sleep sau 15 phút**: Nếu không có traffic 15 phút, app sẽ sleep
- **Lần đầu wake up**: Có thể mất 30-60 giây để wake up
- **File uploads**: Free tier có persistent storage, nhưng nên backup

### 2. Database

- **PostgreSQL**: Render cung cấp PostgreSQL free
- **Migration**: Database sẽ tự tạo tables khi app chạy lần đầu (nếu dùng SQLAlchemy `create_all`)
- **Backup**: Nên backup database định kỳ

### 3. File Uploads

- **Local storage**: Render có persistent storage, files sẽ không bị mất
- **URL**: `https://your-app.onrender.com/static/filename.jpg`
- **Backup**: Nên backup folder `uploads/` định kỳ

### 4. Socket.IO

- ✅ **Hoạt động tốt** trên Render
- ✅ WebSocket connections được hỗ trợ đầy đủ

### 5. Background Jobs

- ✅ **APScheduler hoạt động tốt** trên Render
- ✅ Jobs sẽ chạy liên tục (trừ khi app sleep)

## 🐛 Troubleshooting

### App không start được

1. Kiểm tra **Logs** trong Render Dashboard
2. Kiểm tra `requirements.txt` có đúng không
3. Kiểm tra `Start Command` có đúng không
4. Kiểm tra Python version (Render hỗ trợ Python 3.7+)

### Database connection error

1. Kiểm tra `DATABASE_URL` có đúng format không
2. Kiểm tra database đã được tạo chưa
3. Kiểm tra database và web service cùng region

### Port error

- Render tự động set `PORT` environment variable
- Đảm bảo code lấy port từ `os.environ.get('PORT')`

### App sleep quá lâu

- Free tier sẽ sleep sau 15 phút không có traffic
- Có thể dùng [UptimeRobot](https://uptimerobot.com) (free) để ping app mỗi 5 phút

## 📊 So sánh với Vercel

| Tính năng | Render (Free) | Vercel (Free) |
|-----------|---------------|---------------|
| **Flask Support** | ✅ | ✅ |
| **Socket.IO** | ✅ | ⚠️ Hạn chế |
| **Background Jobs** | ✅ | ❌ |
| **File Uploads Local** | ✅ | ❌ |
| **Sleep** | ⚠️ 15 phút | ✅ Không |
| **Deploy** | ✅ Dễ | ✅ Rất dễ |
| **Database** | ✅ PostgreSQL free | ❌ Tự setup |

## 🎯 Kết luận

**Render free tier là lựa chọn TỐT NHẤT cho project học tập** vì:
- ✅ Miễn phí hoàn toàn
- ✅ Hỗ trợ đầy đủ tất cả tính năng
- ✅ Dễ deploy
- ⚠️ Chỉ có nhược điểm là sleep sau 15 phút (OK cho demo)

## 📚 Tài liệu tham khảo

- [Render Documentation](https://render.com/docs)
- [Deploy Python on Render](https://render.com/docs/deploy-python)
- [Render PostgreSQL](https://render.com/docs/databases)


