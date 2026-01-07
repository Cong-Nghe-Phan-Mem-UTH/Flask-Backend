# Hướng dẫn cài đặt Database Studio

## 🔧 Cài đặt Dependencies

### Bước 1: Kích hoạt Virtual Environment

**MacOS/Linux:**
```bash
cd src
source .venv/bin/activate
```

**Windows:**
```bash
cd src
.venv\Scripts\activate
```

Sau khi kích hoạt, bạn sẽ thấy `(.venv)` ở đầu dòng terminal.

### Bước 2: Cài đặt Flask-Admin

```bash
pip install Flask-Admin>=1.6
```

Hoặc cài đặt tất cả dependencies:
```bash
pip install -r requirements.txt
```

### Bước 3: Chạy Database Studio

```bash
python admin_studio.py
```

Database Studio sẽ chạy tại: **http://localhost:5555**

## 🚀 Cách nhanh (All-in-one)

**MacOS/Linux:**
```bash
cd src
source .venv/bin/activate && pip install Flask-Admin>=1.6 && python admin_studio.py
```

**Windows:**
```bash
cd src
.venv\Scripts\activate && pip install Flask-Admin>=1.6 && python admin_studio.py
```

## ⚠️ Lưu ý

- Luôn kích hoạt virtual environment trước khi chạy
- Nếu gặp lỗi "command not found: pip", hãy dùng `pip3` hoặc `python3 -m pip`
- Đảm bảo đã có file `.env` trong thư mục `src/` với cấu hình database

## 🔐 Đăng nhập

- URL: http://localhost:5555
- Email: `admin@order.com` (hoặc email Owner của bạn)
- Password: `123456` (hoặc password Owner của bạn)

