# Hướng dẫn sử dụng Postman để Test Upload Ảnh

## Bước 1: Tải và cài đặt Postman

### MacOS:

1. Truy cập: https://www.postman.com/downloads/
2. Click **"Download for Mac"**
3. Mở file `.dmg` đã tải
4. Kéo **Postman** vào **Applications**
5. Mở Postman từ Applications

**Hoặc từ App Store:**

- Mở App Store
- Tìm "Postman"
- Click **"Get"** hoặc **"Install"**

---

## Bước 2: Đảm bảo Server đang chạy

**Mở Terminal và chạy:**

```bash
cd /Users/mac/Documents/project_cnpm/Flask-BackEnd/src
source .venv/bin/activate
python app.py
```

**Giữ terminal này mở** - bạn sẽ thấy server chạy tại `http://localhost:4000`

---

## Bước 3: Test Endpoint Đơn Giản (Không cần đăng nhập)

### 3.1. Tạo Request mới

1. Mở Postman
2. Click nút **"New"** (góc trên bên trái)
3. Chọn **"HTTP Request"**
4. Hoặc click **"+"** tab để tạo tab mới

### 3.2. Cấu hình Request

1. **Method:** Chọn **POST** (dropdown bên trái)
2. **URL:** Gõ `http://localhost:4000/media/test`
3. **Body tab:** Click tab **"Body"** (bên dưới URL)
4. Chọn **"form-data"** (radio button)
5. **Key:** Gõ `file`
6. **Type:** Click dropdown bên phải Key → Chọn **"File"** (thay vì "Text")
7. **Value:** Click **"Select Files"** → Chọn file ảnh từ Finder
8. Click nút **"Send"** (màu xanh, góc trên bên phải)

### 3.3. Xem kết quả

**Response sẽ hiển thị ở phần dưới:**

```json
{
  "message": "Media route is working",
  "method": "POST",
  "content_type": "multipart/form-data; boundary=...",
  "has_files": true,
  "file_keys": ["file"],
  "form_keys": []
}
```

**✅ Nếu thấy kết quả này** → Route hoạt động tốt!

---

## Bước 4: Đăng nhập để lấy Token

### 4.1. Tạo Request mới

1. Click **"New"** hoặc **"+"** để tạo request mới
2. Đặt tên: **"Login"** (click vào "New Request" để đổi tên)

### 4.2. Cấu hình Request

1. **Method:** Chọn **POST**
2. **URL:** Gõ `http://localhost:4000/auth/login`
3. **Headers tab:** Click tab **"Headers"**
   - Key: `Content-Type`
   - Value: `application/json`
4. **Body tab:** Click tab **"Body"**
   - Chọn **"raw"** (radio button)
   - Dropdown bên phải: Chọn **"JSON"**
   - **QUAN TRỌNG:** Chỉ gõ JSON object, KHÔNG gõ chữ "json" ở đầu!
   - Gõ nội dung:

```json
{
  "email": "admin@order.com",
  "password": "123456"
}
```

**⚠️ LỖI THƯỜNG GẶP:**

- ❌ **SAI:** Gõ `json` rồi mới gõ `{...}`
- ✅ **ĐÚNG:** Chỉ gõ `{...}` thôi (Postman đã biết là JSON rồi vì bạn chọn "JSON" ở dropdown)

5. Click **"Send"**

### 4.3. Copy Token

**Response sẽ có dạng:**

```json
{
  "message": "Đăng nhập thành công",
  "data": {
    "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "account": {...}
  }
}
```

**Copy `accessToken`:**

1. Tìm dòng `"accessToken": "eyJ..."`
2. Copy toàn bộ chuỗi token (từ `eyJ` đến `...` trước dấu `"`)

**Lưu ý:** Token này sẽ dùng cho bước tiếp theo!

---

## Bước 5: Upload Ảnh (Cần Token)

### 5.1. Tạo Request mới

1. Click **"New"** hoặc **"+"** để tạo request mới
2. Đặt tên: **"Upload Image"**

### 5.2. Cấu hình Request

1. **Method:** Chọn **POST**
2. **URL:** Gõ `http://localhost:4000/media/upload`
3. **Headers tab:** Click tab **"Headers"**

   - Key: `Authorization`
   - Value: `Bearer YOUR_TOKEN` (thay `YOUR_TOKEN` bằng token từ bước 4)

   **Ví dụ:**

   ```
   Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
   ```

4. **Body tab:** Click tab **"Body"**
   - Chọn **"form-data"** (radio button)
   - **Key:** Gõ `file`
   - **Type:** Chọn **"File"** (dropdown bên phải)
   - **Value:** Click **"Select Files"** → Chọn file ảnh từ Finder
5. Click **"Send"**

### 5.3. Xem kết quả

**Response thành công:**

```json
{
  "message": "Upload ảnh thành công",
  "data": "http://localhost:4000/static/abc123def456.jpg"
}
```

**✅ URL trong `data` là URL của ảnh đã upload!**

Bạn có thể:

- Copy URL này
- Dán vào browser để xem ảnh
- Dùng URL này khi tạo/cập nhật món ăn hoặc avatar

---

## ⚠️ Cảnh báo về File trong Postman

### Nếu thấy cảnh báo: "The file above is not in your working directory"

**Đây KHÔNG phải lỗi!** Request vẫn hoạt động bình thường.

**Cảnh báo này có nghĩa:**

- File bạn chọn nằm ngoài working directory của Postman
- Khi share request với người khác, họ sẽ không thấy file này

**Cách xử lý:**

#### Cách 1: Bỏ qua (Khuyến nghị - nếu chỉ test local)

- **Click "Send" bình thường** - request vẫn hoạt động
- Cảnh báo này không ảnh hưởng đến việc upload
- Chỉ cần quan tâm nếu bạn muốn share request với người khác

#### Cách 2: Upload file lên Postman (Nếu muốn share request)

1. Trong Body → form-data → Key `file`
2. Thay vì chọn "Select Files", click **"Upload"** hoặc **"Choose Files"**
3. Postman sẽ upload file lên và lưu trong request
4. Khi share request, người khác sẽ thấy file

#### Cách 3: Set up Working Directory (Nếu thường xuyên dùng file)

1. Click **"Settings"** (icon bánh răng, góc trên bên phải)
2. Chọn **"General"** tab
3. Tìm **"Working Directory"**
4. Click **"Browse"** và chọn thư mục chứa file ảnh của bạn
5. Click **"Save"**

**Lưu ý:** Cách 1 (bỏ qua) là đủ nếu bạn chỉ test API. Cảnh báo này không ảnh hưởng đến kết quả upload!

---

## Mẹo: Lưu Request để dùng lại

### Lưu Request vào Collection:

1. Click **"Save"** (góc trên bên phải)
2. Tạo Collection mới:
   - Click **"New Collection"**
   - Đặt tên: **"Flask API"**
   - Click **"Create"**
3. Chọn Collection vừa tạo
4. Click **"Save"**

**Lần sau:**

- Click Collection **"Flask API"** ở sidebar bên trái
- Click request để mở lại
- Chỉ cần thay token và click **"Send"**

---

## Mẹo: Dùng Environment Variables cho Token

### Tạo Environment:

1. Click icon **"Environments"** (bên trái, icon hình cái bánh răng)
2. Click **"+"** để tạo mới
3. Đặt tên: **"Flask Local"**
4. Thêm biến:
   - **Variable:** `token`
   - **Initial Value:** (để trống)
   - **Current Value:** (để trống)
5. Click **"Save"**

### Sử dụng Environment:

1. Chọn Environment: Dropdown góc trên bên phải → Chọn **"Flask Local"**
2. Trong request Upload:
   - Headers → Value: `Bearer {{token}}`
3. Sau khi login:
   - Copy token từ response
   - Vào Environment **"Flask Local"**
   - Paste vào **Current Value** của biến `token`
   - Click **"Save"**

**Lần sau chỉ cần chọn Environment, không cần copy/paste token nữa!**

---

## Troubleshooting

### Lỗi: "Could not get response"

**Nguyên nhân:** Server chưa chạy

**Giải pháp:**

- Kiểm tra server có đang chạy không
- Xem terminal có hiển thị `Running on http://0.0.0.0:4000` không
- Nếu chưa, chạy lại server (Bước 2)

### Lỗi: "401 Unauthorized" hoặc "Access token không hợp lệ"

**Nguyên nhân:** Token sai, thiếu, hoặc hết hạn

**Giải pháp từng bước:**

#### Bước 1: Kiểm tra format Header

- Key: `Authorization`
- Value: `Bearer YOUR_TOKEN` (có dấu cách sau "Bearer")
- **KHÔNG có dấu ngoặc kép** quanh token
- **KHÔNG có khoảng trắng thừa**

#### Bước 2: Kiểm tra token đầy đủ

- Token thường rất dài (200-300 ký tự)
- Bắt đầu bằng `eyJ`
- Nếu token ngắn hoặc có `...` → copy lại, có thể bị cắt

#### Bước 3: Copy token đúng cách

1. Trong response login, **double-click** vào token để chọn toàn bộ
2. Copy (Cmd+C)
3. Paste vào Header Value: `Bearer ` + paste token

#### Bước 4: Đăng nhập lại nếu vẫn lỗi

- Token có thể đã hết hạn (thường hết hạn sau 15 phút)
- Đăng nhập lại (Bước 4) để lấy token mới
- Copy token mới và thử lại

#### Bước 5: Kiểm tra server logs

- Xem terminal chạy server có lỗi gì không
- Có thể thấy chi tiết lỗi trong logs

### Lỗi: "Không tìm thấy file"

**Nguyên nhân:** File chưa được chọn

**Giải pháp:**

- Kiểm tra Body → form-data → Key `file` có type là **"File"** không
- Click **"Select Files"** và chọn lại file
- Đảm bảo file là ảnh (png, jpg, jpeg, gif, webp)

### Lỗi: "File không hợp lệ"

**Nguyên nhân:** File không phải ảnh hoặc định dạng không hỗ trợ

**Giải pháp:**

- Chỉ chấp nhận: png, jpg, jpeg, gif, webp
- Kiểm tra extension của file

### Response trống hoặc lỗi 500

**Nguyên nhân:** Lỗi server

**Giải pháp:**

- Xem logs trong terminal chạy server
- Kiểm tra có lỗi gì không
- Thử lại với file ảnh khác

---

## Tóm tắt các bước:

1. ✅ **Tải Postman** và cài đặt
2. ✅ **Chạy server** Flask (Terminal)
3. ✅ **Test endpoint đơn giản** (`/media/test`) - không cần auth
4. ✅ **Đăng nhập** (`/auth/login`) - lấy token
5. ✅ **Upload ảnh** (`/media/upload`) - dùng token

---

## Video hướng dẫn (nếu có)

Nếu bạn muốn xem video hướng dẫn, có thể tìm trên YouTube:

- "How to use Postman for file upload"
- "Postman multipart form-data tutorial"

---

## Liên hệ

Nếu vẫn gặp vấn đề, vui lòng cung cấp:

1. Screenshot của Postman request
2. Response từ Postman
3. Logs từ terminal chạy server
