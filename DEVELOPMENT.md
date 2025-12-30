# Development Guide

## 🚀 Chạy Development Servers

### Cách 1: Chạy cả Backend và Frontend cùng lúc (Khuyến nghị)

**MacOS/Linux:**

```bash
cd Flask-BackEnd
chmod +x scripts/start_dev.sh
./scripts/start_dev.sh
```

**Windows:**

```cmd
cd Flask-BackEnd
scripts\start_dev.bat
```

### Cách 2: Chạy riêng từng server

**Backend (Flask):**

```bash
cd Flask-BackEnd/src
source .venv/bin/activate
python app.py
```

Backend sẽ chạy tại: `http://localhost:4000`

**Frontend (Next.js):**

```bash
cd NextJs-Super-FrontEnd
npm run dev
```

Frontend sẽ chạy tại: `http://localhost:3000`

### Cách 3: Sử dụng VS Code Tasks

1. Mở Command Palette (`Cmd+Shift+P` / `Ctrl+Shift+P`)
2. Chọn "Tasks: Run Task"
3. Chọn một trong các tasks:
   - `Start Backend (Flask)` - Chỉ chạy backend
   - `Start Frontend (Next.js)` - Chỉ chạy frontend
   - `Start All (Backend + Frontend)` - Chạy cả 2

## 📁 Cấu trúc Project

```
project_cnpm/
├── Flask-BackEnd/          # Flask Backend API
│   ├── src/
│   │   ├── api/            # API routes, middleware
│   │   ├── services/       # Business logic
│   │   ├── infrastructure/ # Database, models
│   │   └── ...
│   └── scripts/            # Development scripts
│
└── NextJs-Super-FrontEnd/  # Next.js Frontend
    ├── src/
    │   ├── app/           # Next.js app router
    │   ├── components/    # React components
    │   └── ...
    └── package.json
```

## 🔧 Configuration

### Backend Environment Variables

File: `Flask-BackEnd/src/.env`

```env
DATABASE_URL=mssql+pymssql://sa:Aa123456@127.0.0.1:1433/FlaskApiDB
ACCESS_TOKEN_SECRET=your-secret-key
REFRESH_TOKEN_SECRET=your-refresh-token-secret
PORT=4000
CLIENT_URL=http://localhost:3000
```

### Frontend Configuration

**Tạo file `.env.local` trong thư mục `NextJs-Super-FrontEnd/`:**

```env
# API Endpoint - Flask Backend
NEXT_PUBLIC_API_ENDPOINT=http://localhost:4000

# Frontend URL
NEXT_PUBLIC_URL=http://localhost:3000

# Google OAuth (nếu có)
NEXT_PUBLIC_GOOGLE_CLIENT_ID=your-google-client-id
NEXT_PUBLIC_GOOGLE_AUTHORIZED_REDIRECT_URI=http://localhost:3000/login-success
```

**Lưu ý:**

- `NEXT_PUBLIC_API_ENDPOINT` phải trỏ đến Flask backend (`http://localhost:4000`)
- Frontend sử dụng biến này để:
  - Kết nối Socket.IO trực tiếp đến Flask backend
  - Next.js API routes gọi đến Flask backend
  - Một số API calls trực tiếp đến Flask backend

## 🐛 Troubleshooting

### Backend không chạy được

1. Kiểm tra virtual environment:

   ```bash
   cd Flask-BackEnd/src
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Kiểm tra database connection:

   ```bash
   python -c "from config import Config; print(Config.DATABASE_URI)"
   ```

3. Kiểm tra port 4000 có đang được sử dụng:
   ```bash
   lsof -i :4000  # MacOS/Linux
   netstat -ano | findstr :4000  # Windows
   ```

### Frontend không kết nối được Backend

1. Kiểm tra CORS settings trong `Flask-BackEnd/src/config.py`
2. Kiểm tra `CLIENT_URL` trong `.env` có đúng không
3. Kiểm tra API URL trong frontend config

### Port đã được sử dụng

Thay đổi port trong:

- Backend: `Flask-BackEnd/src/.env` → `PORT=4001`
- Frontend: `NextJs-Super-FrontEnd/package.json` → `"dev": "next dev -p 3001"`

## 📝 Notes

- Backend chạy trên port **4000**
- Frontend chạy trên port **3000**
- Database: MSSQL tại `127.0.0.1:1433`
- Socket.IO đã được tích hợp cho real-time features
