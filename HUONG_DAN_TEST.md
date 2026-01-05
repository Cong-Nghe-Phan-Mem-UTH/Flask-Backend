# Hướng dẫn Test Upload Ảnh - Từng Bước

## Bước 0: Kiểm tra Server có đang chạy không

### Mở Terminal (MacOS):

1. Nhấn `Cmd + Space` để mở Spotlight
2. Gõ "Terminal" và nhấn Enter
3. Hoặc vào Applications > Utilities > Terminal

### Kiểm tra server:

```bash
# Kiểm tra xem server có đang chạy không
curl http://localhost:4000/test/

# Nếu thấy response thì server đang chạy
# Nếu thấy "Connection refused" thì server chưa chạy
```

### Nếu server chưa chạy, chạy server:

**Mở Terminal mới và chạy:**

```bash
# Di chuyển vào thư mục project
cd /Users/mac/Documents/project_cnpm/Flask-BackEnd/src

# Kích hoạt virtual environment
source .venv/bin/activate

# Chạy server
python app.py
```

**Giữ terminal này mở** - bạn sẽ thấy logs ở đây.

---

## Bước 1: Test Endpoint Đơn Giản (Không cần đăng nhập)

**Mở Terminal MỚI** (giữ terminal chạy server mở):

### Cách 1: Dùng file có sẵn trong project (Dễ nhất)

```bash
# Test với file có sẵn trong uploads
curl -X POST http://localhost:4000/media/test \
  -F "file=@/Users/mac/Documents/project_cnpm/Flask-BackEnd/src/uploads/0fd142ce3e694f57badf5447325d12ce.jpg"
```

### Cách 2: Dùng file của bạn

**Nếu gặp lỗi "Failed to open/read local data":**

1. **Kéo thả file vào Terminal:**

   - Gõ: `curl -X POST http://localhost:4000/media/test -F "file=@`
   - **Kéo file ảnh từ Finder vào Terminal** (sau dấu @)
   - Terminal sẽ tự điền đường dẫn
   - Hoàn thành: `"`

2. **Hoặc copy đường dẫn từ Finder:**

   - Click chuột phải vào file → Giữ **Option** → Chọn **"Copy ... as Pathname"**
   - Dán vào lệnh

3. **Hoặc dùng đường dẫn tương đối:**

```bash
curl -X POST http://localhost:4000/media/test \
  -F "file=@~/Desktop/your-image.jpg"
```

**Kết quả mong đợi:**

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

**Nếu thấy kết quả này** → Route hoạt động tốt, vấn đề có thể ở authentication.

---

## Bước 2: Đăng nhập để lấy Token

**Trong Terminal mới (không phải terminal chạy server):**

```bash
# Đăng nhập
curl -X POST http://localhost:4000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@order.com",
    "password": "123456"
  }'
```

**Kết quả sẽ có dạng:**

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

**Copy `accessToken`** từ kết quả (phần sau `"accessToken": "` đến trước `"`)

---

## Bước 3: Upload Ảnh (Cần Token)

**Trong cùng Terminal đó:**

### Cách 1: Dùng file có sẵn (Dễ nhất)

```bash
# Thay YOUR_TOKEN bằng token vừa copy
curl -X POST http://localhost:4000/media/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@/Users/mac/Documents/project_cnpm/Flask-BackEnd/src/uploads/0fd142ce3e694f57badf5447325d12ce.jpg"
```

### Cách 2: Dùng file của bạn

**Nếu gặp lỗi "Failed to open/read local data":**

1. **Kéo thả file vào Terminal:**

   - Gõ: `curl -X POST http://localhost:4000/media/upload -H "Authorization: Bearer YOUR_TOKEN" -F "file=@`
   - **Kéo file ảnh từ Finder vào Terminal**
   - Hoàn thành: `"`

2. **Hoặc dùng đường dẫn tương đối:**

```bash
curl -X POST http://localhost:4000/media/upload \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@~/Desktop/your-image.jpg"
```

**Lưu ý:**

- Thay `YOUR_TOKEN` bằng token thật từ bước 2
- Nếu không chắc đường dẫn, dùng **Cách 1** (file có sẵn) hoặc **Postman** (xem bên dưới)

**Kết quả mong đợi:**

```json
{
  "message": "Upload ảnh thành công",
  "data": "http://localhost:4000/static/abc123def456.jpg"
}
```

---

## Cách Dễ Hơn: Dùng Postman

Nếu không muốn dùng Terminal, có thể dùng **Postman**:

### 1. Tải Postman:

- Truy cập: https://www.postman.com/downloads/
- Hoặc tải từ App Store trên Mac

### 2. Test Endpoint Đơn Giản:

- Method: `POST`
- URL: `http://localhost:4000/media/test`
- Body → chọn `form-data`
- Key: `file` (type: File)
- Value: Chọn file ảnh
- Click **Send**

### 3. Đăng nhập:

- Method: `POST`
- URL: `http://localhost:4000/auth/login`
- Headers: `Content-Type: application/json`
- Body → chọn `raw` → `JSON`
- Nội dung:

```json
{
  "email": "admin@order.com",
  "password": "123456"
}
```

- Click **Send**
- Copy `accessToken` từ response

### 4. Upload Ảnh:

- Method: `POST`
- URL: `http://localhost:4000/media/upload`
- Headers:
  - Key: `Authorization`
  - Value: `Bearer YOUR_TOKEN` (thay YOUR_TOKEN bằng token từ bước 3)
- Body → chọn `form-data`
- Key: `file` (type: File)
- Value: Chọn file ảnh
- Click **Send**

---

## Xem Logs

**Trong terminal đang chạy server**, bạn sẽ thấy logs như:

```
📤 Upload request - Content-Type: multipart/form-data; boundary=...
📤 Upload request - Method: POST
📤 Upload request - Has files: True
📤 Upload request - Files keys: ['file']
✅ File saved successfully. Size: 123456 bytes
✅ Upload URL: http://localhost:4000/static/abc123.jpg
```

Nếu có lỗi, logs sẽ hiển thị chi tiết.

---

## Troubleshooting

### Lỗi: "Connection refused"

→ Server chưa chạy, chạy lại server (Bước 0)

### Lỗi: "Access token không hợp lệ"

→ Token đã hết hạn, đăng nhập lại lấy token mới

### Lỗi: "Không tìm thấy file"

→ Kiểm tra:

- File có tồn tại không?
- Đường dẫn có đúng không?
- Field name có đúng là `file` không?

### Lỗi: "File không hợp lệ"

→ Chỉ chấp nhận: png, jpg, jpeg, gif, webp

---

## 🎯 Test QR Code Gọi Món Từ Điện Thoại (Trải Nghiệm Thực Tế)

**Muốn test như khách hàng thực tế? Quét QR code bằng điện thoại để vào trang gọi món?**

👉 **Xem hướng dẫn chi tiết:** [scripts/test_qr_phone.md](./scripts/test_qr_phone.md)

**Hoặc chạy script tự động:**

```bash
cd /Users/mac/Documents/project_cnpm/Flask-BackEnd
./scripts/test_qr_phone.sh
```

**Tóm tắt nhanh:**

1. Lấy IP: `ipconfig getifaddr en0`
2. Chạy Backend: `cd src && DOMAIN=YOUR_IP python app.py`
3. Chạy Frontend: `cd ../NextJs-Super-FrontEnd && npm run dev -- -H YOUR_IP`
4. Lấy thông tin bàn: `curl http://localhost:4000/tables/`
5. Tạo QR code với URL: `http://YOUR_IP:3000/vi/tables/1?token=YOUR_TOKEN`
6. Quét bằng điện thoại (cùng WiFi)

---

## Test Từ Frontend (Nếu có)

Nếu bạn có frontend React/Next.js, có thể test trực tiếp từ đó:

```javascript
const handleUpload = async (file) => {
  const formData = new FormData();
  formData.append("file", file);

  const response = await fetch("http://localhost:4000/media/upload", {
    method: "POST",
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    body: formData,
  });

  const result = await response.json();
  console.log(result);
};
```

---

## Test QR Code Gọi Món Từ Điện Thoại

### Bước 1: Lấy IP Address của Máy Tính

**Trên MacOS:**

```bash
# Mở Terminal và chạy:
ifconfig | grep "inet " | grep -v 127.0.0.1
```

Hoặc đơn giản hơn:

```bash
ipconfig getifaddr en0
```

**Kết quả sẽ có dạng:** `192.168.1.100` (đây là IP local của bạn)

**Lưu ý:** Đảm bảo điện thoại và máy tính cùng kết nối vào **cùng một mạng WiFi**.

---

### Bước 2: Chạy Server với IP Address

**Cách 1: Sửa file `.env` (Khuyến nghị)**

Thêm hoặc sửa trong file `src/.env`:

```env
DOMAIN=192.168.1.100  # Thay bằng IP của bạn
PORT=4000
```

Sau đó chạy lại server:

```bash
cd /Users/mac/Documents/project_cnpm/Flask-BackEnd/src
source .venv/bin/activate
python app.py
```

**Cách 2: Chạy với biến môi trường**

```bash
cd /Users/mac/Documents/project_cnpm/Flask-BackEnd/src
source .venv/bin/activate
DOMAIN=192.168.1.100 python app.py
```

**Lưu ý:** Thay `192.168.1.100` bằng IP thực tế của bạn.

---

### Bước 3: Lấy Thông Tin Bàn (Table Number và Token)

**Cách 1: Dùng API (Không cần đăng nhập)**

Mở Terminal mới và chạy:

```bash
# Lấy danh sách tất cả bàn
curl http://localhost:4000/tables/
```

**Kết quả sẽ có dạng:**

```json
{
  "data": [
    {
      "number": 1,
      "capacity": 4,
      "status": "Available",
      "token": "abc123def456ghi789",
      "createdAt": "2024-01-01T00:00:00",
      "updatedAt": "2024-01-01T00:00:00"
    },
    {
      "number": 2,
      "capacity": 2,
      "status": "Available",
      "token": "xyz789uvw456rst123",
      "createdAt": "2024-01-01T00:00:00",
      "updatedAt": "2024-01-01T00:00:00"
    }
  ],
  "message": "Lấy danh sách bàn thành công!"
}
```

**Ghi lại:**

- `number`: Số bàn (ví dụ: `1`)
- `token`: Token của bàn (ví dụ: `abc123def456ghi789`)

**Cách 2: Lấy thông tin bàn cụ thể**

```bash
# Thay 1 bằng số bàn bạn muốn
curl http://localhost:4000/tables/1
```

---

### Bước 4: Tạo QR Code (Tùy chọn)

Bạn có thể tạo QR code chứa URL để khách hàng quét. QR code sẽ chứa URL dạng:

```
http://192.168.1.100:4000/guest/login?table=1&token=abc123def456ghi789
```

**Hoặc nếu có frontend:**

```
http://192.168.1.100:3000/guest/login?table=1&token=abc123def456ghi789
```

**Tạo QR Code online:**

- Truy cập: https://www.qr-code-generator.com/
- Dán URL vào
- Tải QR code về và in ra

---

### Bước 5: Test Từ Điện Thoại

#### **Cách 1: Test Trực Tiếp với API (Dùng App như Postman Mobile)**

1. **Tải app Postman** trên điện thoại (iOS/Android)

2. **Đăng nhập Guest:**

   - Method: `POST`
   - URL: `http://192.168.1.100:4000/guest/auth/login`
   - Headers: `Content-Type: application/json`
   - Body (raw JSON):

   ```json
   {
     "tableNumber": 1,
     "token": "abc123def456ghi789",
     "name": "Khách hàng test"
   }
   ```

   - Click **Send**

   **Kết quả:**

   ```json
   {
     "message": "Đăng nhập thành công",
     "data": {
       "guest": {
         "id": 1,
         "name": "Khách hàng test",
         "role": "Guest",
         "tableNumber": 1
       },
       "accessToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
       "refreshToken": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
     }
   }
   ```

   **Copy `accessToken`** để dùng cho các request tiếp theo.

3. **Xem danh sách món ăn:**

   - Method: `GET`
   - URL: `http://192.168.1.100:4000/dishes/`
   - Click **Send**

4. **Đặt món:**

   - Method: `POST`
   - URL: `http://192.168.1.100:4000/guest/orders`
   - Headers:
     - `Content-Type: application/json`
     - `Authorization: Bearer YOUR_ACCESS_TOKEN` (thay bằng token từ bước 2)
   - Body (raw JSON):

   ```json
   [
     {
       "dishId": 1,
       "quantity": 2
     },
     {
       "dishId": 2,
       "quantity": 1
     }
   ]
   ```

   - Click **Send**

5. **Xem đơn hàng của mình:**

   - Method: `GET`
   - URL: `http://192.168.1.100:4000/guest/orders`
   - Headers: `Authorization: Bearer YOUR_ACCESS_TOKEN`
   - Click **Send**

#### **Cách 2: Test Với Frontend (Nếu có)**

1. **Đảm bảo Frontend cũng chạy và accessible từ điện thoại:**

   - Sửa file config frontend để trỏ đến: `http://192.168.1.100:4000`
   - Chạy frontend với IP:

   ```bash
   # Trong thư mục NextJs-Super-FrontEnd
   npm run dev -- -H 192.168.1.100
   ```

2. **Mở trình duyệt trên điện thoại:**

   - Truy cập: `http://192.168.1.100:3000` (hoặc port của frontend)
   - Quét QR code hoặc nhập thông tin bàn
   - Test các chức năng gọi món

#### **Cách 3: Tạo Trang Test Đơn Giản**

Tạo file HTML đơn giản để test:

```html
<!DOCTYPE html>
<html>
  <head>
    <title>Test QR Code - Gọi Món</title>
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  </head>
  <body>
    <h1>Đăng nhập bàn</h1>
    <input type="number" id="tableNumber" placeholder="Số bàn" value="1" />
    <input
      type="text"
      id="token"
      placeholder="Token"
      value="abc123def456ghi789"
    />
    <input type="text" id="name" placeholder="Tên khách" value="Khách test" />
    <button onclick="login()">Đăng nhập</button>

    <div id="result"></div>
    <div id="dishes"></div>

    <script>
      const API_URL = "http://192.168.1.100:4000"; // Thay bằng IP của bạn
      let accessToken = "";

      async function login() {
        const tableNumber = document.getElementById("tableNumber").value;
        const token = document.getElementById("token").value;
        const name = document.getElementById("name").value;

        try {
          const response = await fetch(`${API_URL}/guest/auth/login`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
              tableNumber: parseInt(tableNumber),
              token,
              name,
            }),
          });

          const data = await response.json();
          if (response.ok) {
            accessToken = data.data.accessToken;
            document.getElementById("result").innerHTML =
              '<p style="color: green;">Đăng nhập thành công!</p>';
            loadDishes();
          } else {
            document.getElementById("result").innerHTML =
              '<p style="color: red;">Lỗi: ' + data.message + "</p>";
          }
        } catch (error) {
          document.getElementById("result").innerHTML =
            '<p style="color: red;">Lỗi kết nối: ' + error.message + "</p>";
        }
      }

      async function loadDishes() {
        try {
          const response = await fetch(`${API_URL}/dishes/`);
          const data = await response.json();
          let html = "<h2>Danh sách món:</h2><ul>";
          data.data.forEach((dish) => {
            html += `<li>${dish.name} - ${dish.price}đ 
                        <button onclick="orderDish(${dish.id})">Đặt món</button></li>`;
          });
          html += "</ul>";
          document.getElementById("dishes").innerHTML = html;
        } catch (error) {
          console.error("Lỗi load món:", error);
        }
      }

      async function orderDish(dishId) {
        if (!accessToken) {
          alert("Vui lòng đăng nhập trước!");
          return;
        }

        try {
          const response = await fetch(`${API_URL}/guest/orders`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${accessToken}`,
            },
            body: JSON.stringify([{ dishId, quantity: 1 }]),
          });

          const data = await response.json();
          if (response.ok) {
            alert("Đặt món thành công!");
          } else {
            alert("Lỗi: " + data.message);
          }
        } catch (error) {
          alert("Lỗi: " + error.message);
        }
      }
    </script>
  </body>
</html>
```

Lưu file này và mở bằng trình duyệt trên điện thoại.

---

### Troubleshooting

#### **Lỗi: "Connection refused" hoặc không kết nối được**

1. **Kiểm tra firewall:**

   - MacOS: System Preferences → Security & Privacy → Firewall
   - Đảm bảo cho phép kết nối đến port 4000

2. **Kiểm tra cùng mạng WiFi:**

   - Điện thoại và máy tính phải cùng WiFi
   - Không dùng mobile data trên điện thoại

3. **Kiểm tra IP address:**
   - Chạy lại `ipconfig getifaddr en0` để xác nhận IP
   - Đảm bảo IP không thay đổi

#### **Lỗi: "Bàn không tồn tại hoặc mã token không đúng"**

- Kiểm tra lại `tableNumber` và `token` từ bước 3
- Đảm bảo bàn có status là `Available` (không phải `Hidden` hoặc `Reserved`)

#### **Lỗi: "Access token không hợp lệ"**

- Token đã hết hạn (guest token hết hạn sau 1 giờ)
- Đăng nhập lại để lấy token mới

---

### Tips

1. **Dùng ngrok để test từ xa (không cần cùng WiFi):**

   ```bash
   # Cài ngrok: brew install ngrok
   ngrok http 4000
   ```

   Sẽ có URL dạng: `https://abc123.ngrok.io` - dùng URL này thay vì IP local

2. **Tạo nhiều bàn để test:**

   ```bash
   # Đăng nhập admin trước
   curl -X POST http://localhost:4000/tables/ \
     -H "Authorization: Bearer ADMIN_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"number": 3, "capacity": 4}'
   ```

3. **Xem logs server** để debug khi có lỗi
