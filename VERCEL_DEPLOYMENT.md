# Hướng dẫn Deploy Flask Backend lên Vercel

## ✅ Vercel HỖ TRỢ Flask/Python

**Vercel có hỗ trợ Flask** thông qua Python runtime (`@vercel/python`). Bạn hoàn toàn có thể deploy Flask lên Vercel!

## 📋 Tổng quan

Dự án này đã được cấu hình để deploy lên Vercel. Tuy nhiên, có một số điểm cần lưu ý:

> 💡 **Lưu ý**: Nếu bạn cần Socket.IO, background jobs, hoặc file uploads local, hãy xem file `DEPLOYMENT_COMPARISON.md` để so sánh các nền tảng khác như Railway, Render, hoặc VPS.

## ⚠️ Lưu ý quan trọng

### 1. Socket.IO và WebSocket
- **Socket.IO có thể không hoạt động đầy đủ** trên Vercel vì môi trường serverless
- Vercel hỗ trợ WebSocket nhưng có thể cần cấu hình thêm
- Nếu cần Socket.IO, cân nhắc sử dụng dịch vụ khác như Railway, Render, hoặc AWS

### 2. File Uploads
- **File uploads vào local filesystem sẽ không hoạt động** trên Vercel
- Vercel sử dụng filesystem tạm thời (ephemeral)
- **KHÔNG đẩy folder `uploads/` lên Vercel** - folder này sẽ bị mất sau mỗi lần deploy
- **URL ảnh sẽ khác nhau giữa local và production:**
  - Local: `http://localhost:4000/static/anh.jpg`
  - Production: `https://your-domain.vercel.app/static/anh.jpg`
- **Giải pháp**: Sử dụng dịch vụ lưu trữ bên ngoài như:
  - AWS S3
  - Cloudinary
  - Vercel Blob Storage
  - Google Cloud Storage

### 3. Background Jobs (APScheduler)
- **Background jobs không hoạt động** trên Vercel serverless
- Cần sử dụng dịch vụ cron job bên ngoài như:
  - Vercel Cron Jobs
  - GitHub Actions
  - External cron service

### 4. Database
- **KHÔNG đẩy file database local lên Vercel** (ví dụ: `dev.db`, `*.db`)
- Database ở local khác với database trên production
- Nếu dùng database local, URL trong database sẽ là `http://localhost:4000/static/...` và không hoạt động trên production
- Đảm bảo database của bạn có thể truy cập từ internet
- SQLite local sẽ không hoạt động, cần database cloud như:
  - PostgreSQL (Vercel Postgres, Supabase, Neon)
  - MySQL (PlanetScale, Railway)
  - SQL Server (Azure SQL)
- **Khởi tạo database mới trên production:**
  - Database sẽ được tạo tự động khi app chạy lần đầu (nếu dùng SQLAlchemy với `Base.metadata.create_all()`)
  - Hoặc chạy migrations nếu có

## 🚀 Các bước deploy

### Bước 1: Cài đặt Vercel CLI (nếu chưa có)

```bash
npm i -g vercel
```

### Bước 2: Đăng nhập Vercel

```bash
vercel login
```

### Bước 3: Deploy

Từ thư mục root của project:

```bash
vercel
```

Hoặc deploy production:

```bash
vercel --prod
```

### Bước 4: Cấu hình Environment Variables

Sau khi deploy, cần cấu hình các biến môi trường trên Vercel Dashboard:

1. Vào project trên Vercel Dashboard
2. Settings → Environment Variables
3. Thêm các biến sau:

```
SECRET_KEY=your-secret-key
ACCESS_TOKEN_SECRET=your-access-token-secret
REFRESH_TOKEN_SECRET=your-refresh-token-secret
DATABASE_URL=your-database-connection-string
INITIAL_EMAIL_OWNER=admin@order.com
INITIAL_PASSWORD_OWNER=123456
CLIENT_URL=https://your-frontend-url.vercel.app
PRODUCTION=true
PRODUCTION_URL=https://your-backend-url.vercel.app
```

### Bước 5: Kiểm tra deployment

Sau khi deploy thành công, bạn sẽ nhận được URL như:
```
https://your-project.vercel.app
```

## 📁 Cấu trúc files cho Vercel

```
Flask-BackEnd/
├── api/
│   └── index.py          # Entry point cho Vercel
├── src/                  # Source code của ứng dụng
├── vercel.json           # Cấu hình Vercel
├── .vercelignore         # Files không deploy
└── requirements.txt      # Python dependencies (cần ở root hoặc src/)
```

## 🔧 Cấu hình bổ sung

### Nếu requirements.txt ở trong src/

Nếu `requirements.txt` nằm trong thư mục `src/`, bạn có thể:

1. Copy `requirements.txt` ra root:
```bash
cp src/requirements.txt requirements.txt
```

2. Hoặc cập nhật `vercel.json` để chỉ định đường dẫn:
```json
{
  "builds": [
    {
      "src": "api/index.py",
      "use": "@vercel/python",
      "config": {
        "maxLambdaSize": "50mb"
      }
    }
  ]
}
```

### Tối ưu hóa cho Vercel

1. **Giảm dependencies**: Loại bỏ các package không cần thiết
2. **Database connection pooling**: Sử dụng connection pooling phù hợp với serverless
3. **Cold start**: Cân nhắc sử dụng Vercel Pro để giảm cold start time

## 🐛 Troubleshooting

### Lỗi import module
- Đảm bảo `PYTHONPATH` được set trong `vercel.json`
- Kiểm tra đường dẫn import trong code

### Lỗi database connection
- Kiểm tra database URL có đúng format không
- Đảm bảo database cho phép kết nối từ internet
- Kiểm tra firewall settings của database

### Lỗi timeout
- Tăng `maxDuration` trong `vercel.json` (tối đa 60s cho Hobby, 300s cho Pro)

### File upload không hoạt động
- Cần migrate sang sử dụng cloud storage
- Cập nhật `media_service.py` để upload lên S3/Cloudinary

## 📚 Tài liệu tham khảo

- [Vercel Python Documentation](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python)
- [Vercel Environment Variables](https://vercel.com/docs/concepts/projects/environment-variables)
- [Flask on Vercel](https://vercel.com/guides/deploying-flask-with-vercel)

## 🔄 Migration Checklist

- [ ] Copy `requirements.txt` ra root nếu cần
- [ ] **KHÔNG đẩy folder `uploads/` lên Vercel** (đã có trong `.vercelignore`)
- [ ] **KHÔNG đẩy file database local** (ví dụ: `*.db`, `dev.db`)
- [ ] Cấu hình database cloud (không dùng SQLite local)
- [ ] Setup cloud storage cho file uploads (S3, Cloudinary, etc.)
- [ ] Cấu hình environment variables trên Vercel
- [ ] Test các endpoints sau khi deploy
- [ ] Kiểm tra URL ảnh trong database phải là production URL
- [ ] Cấu hình custom domain (nếu cần)
- [ ] Setup monitoring và logging

## ⚠️ Lưu ý đặc biệt từ kinh nghiệm deploy

### Về Database và Uploads
- **Database local và production phải tách biệt**: 
  - Database ở local có URL ảnh là `http://localhost:4000/static/...`
  - Database trên production phải có URL ảnh là `https://your-domain.vercel.app/static/...`
  - Nếu copy database từ local lên production, tất cả URL ảnh sẽ bị lỗi

### Về Vercel vs VPS
- **Vercel (Serverless)**: 
  - ✅ Dễ deploy, tự động scale
  - ❌ Không lưu file local, không chạy background jobs tốt
  - ❌ Socket.IO có thể không hoạt động đầy đủ
- **VPS (Traditional Server)**:
  - ✅ Có thể lưu file local, chạy background jobs
  - ✅ Socket.IO hoạt động tốt
  - ❌ Cần tự quản lý server, cấu hình phức tạp hơn
  - 📝 Xem hướng dẫn tại: [blog duthanhduoc.com](https://blog.duthanhduoc.com)

