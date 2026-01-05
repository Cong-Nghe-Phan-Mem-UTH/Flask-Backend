# Hướng dẫn Debug Upload Ảnh

## Các bước kiểm tra

### 1. Kiểm tra endpoint test (không cần auth)

```bash
# Test GET
curl http://localhost:4000/media/test

# Test POST với file
curl -X POST http://localhost:4000/media/test \
  -F "file=@/path/to/image.jpg"
```

Nếu endpoint này hoạt động, vấn đề có thể ở middleware authentication.

### 2. Kiểm tra upload endpoint (cần auth)

**Bước 1: Đăng nhập để lấy token**

```bash
curl -X POST http://localhost:4000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@order.com",
    "password": "123456"
  }'
```

Lưu lại `accessToken` từ response.

**Bước 2: Upload ảnh**

```bash
curl -X POST http://localhost:4000/media/upload \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -F "file=@/path/to/your/image.jpg"
```

### 3. Kiểm tra logs

Xem logs trong terminal nơi chạy Flask server để thấy:
- Request có đến được route không?
- Content-Type là gì?
- Có file trong request không?
- Lỗi gì xảy ra?

### 4. Kiểm tra từ Frontend

**JavaScript/React:**

```javascript
const uploadImage = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await fetch('http://localhost:4000/media/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${accessToken}`
        // KHÔNG set Content-Type, browser sẽ tự động set
      },
      body: formData
    });

    const result = await response.json();
    console.log('Response:', result);
    
    if (!response.ok) {
      console.error('Error:', result);
    }
  } catch (error) {
    console.error('Network error:', error);
  }
};
```

### 5. Các lỗi thường gặp

**Lỗi: "Không tìm thấy file trong request"**
- Kiểm tra: Request có đúng `multipart/form-data` không?
- Kiểm tra: Field name có đúng là `file`, `image`, hoặc `avatar` không?
- Kiểm tra: Có set `Content-Type: multipart/form-data` thủ công không? (KHÔNG nên set, để browser tự động)

**Lỗi: "Access token không hợp lệ"**
- Kiểm tra: Token có hết hạn không?
- Kiểm tra: Header có đúng format `Bearer <token>` không?

**Lỗi: "File quá lớn"**
- Giới hạn: 10MB
- Kiểm tra: File có vượt quá không?

**Lỗi: "File không hợp lệ"**
- Chỉ chấp nhận: png, jpg, jpeg, gif, webp
- Kiểm tra: Extension của file

### 6. Test với Postman

1. Method: `POST`
2. URL: `http://localhost:4000/media/upload`
3. Headers:
   - `Authorization: Bearer YOUR_TOKEN`
   - KHÔNG set `Content-Type` (Postman sẽ tự động set)
4. Body:
   - Chọn `form-data`
   - Key: `file` (type: File)
   - Value: Chọn file ảnh

### 7. Kiểm tra cấu hình

**Kiểm tra MAX_CONTENT_LENGTH:**
```python
# Trong src/config.py
MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # 16MB
```

**Kiểm tra UPLOAD_FOLDER:**
```python
# Trong src/config.py
UPLOAD_FOLDER = os.path.join(_base_dir, 'uploads')
```

**Kiểm tra folder tồn tại:**
```bash
ls -la src/uploads/
```

### 8. Debug nâng cao

Thêm vào `src/api/routes/media_routes.py`:

```python
@app.before_request
def log_request():
    if request.path == '/media/upload':
        print(f"Request method: {request.method}")
        print(f"Content-Type: {request.content_type}")
        print(f"Content-Length: {request.content_length}")
        print(f"Has files: {bool(request.files)}")
```

## Liên hệ

Nếu vẫn không được, vui lòng cung cấp:
1. Logs từ server
2. Response từ API
3. Cách bạn đang gọi API (Frontend code hoặc curl command)


