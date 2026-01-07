# Hướng Dẫn Test QR Code - Khách Hàng & Quản Lý

## 🎯 Mục Tiêu
Test quét QR code với tư cách khách hàng và kiểm tra bên quản lý nhận được thông báo real-time.

---

## 📋 Bước 1: Chuẩn Bị

### 1.1. Lấy IP Address của Máy Tính

**Trên MacOS:**
```bash
ipconfig getifaddr en0
```

Kết quả sẽ có dạng: `192.168.1.100` (ghi lại IP này)

**Lưu ý:** Đảm bảo điện thoại và máy tính **cùng WiFi**.

### 1.2. Lấy Thông Tin Bàn (Table Number và Token)

```bash
curl http://localhost:4000/tables/ | python3 -m json.tool
```

**Ghi lại:**
- `number`: Số bàn (ví dụ: `1`)
- `token`: Token của bàn (ví dụ: `abc123def456ghi789`)

---

## 🚀 Bước 2: Chạy Backend với IP Address

**Mở Terminal 1:**

```bash
cd /Users/mac/Documents/project_cnpm/Flask-BackEnd/src
source .venv/bin/activate

# Thay 192.168.1.100 bằng IP của bạn
DOMAIN=192.168.1.100 python app.py
```

**Hoặc sửa file `src/.env`:**
```env
DOMAIN=192.168.1.100  # Thay bằng IP của bạn
PORT=4000
```

Sau đó chạy:
```bash
python app.py
```

**Kiểm tra:** Mở trình duyệt: `http://192.168.1.100:4000/test/` → Phải thấy response thành công.

---

## 🎨 Bước 3: Chạy Frontend với IP Address

**Mở Terminal 2:**

```bash
cd /Users/mac/Documents/project_cnpm/NextJs-Super-FrontEnd

# Kiểm tra file .env.local
# Đảm bảo có:
# NEXT_PUBLIC_API_ENDPOINT=http://192.168.1.100:4000
# NEXT_PUBLIC_URL=http://192.168.1.100:3000

# Chạy với IP address
npm run dev -- -H 192.168.1.100
```

**Kiểm tra:** Mở trình duyệt: `http://192.168.1.100:3000` → Phải thấy trang chủ.

---

## 📱 Bước 4: Tạo QR Code

### URL Format:
```
http://192.168.1.100:3000/vi/tables/{TABLE_NUMBER}?token={TOKEN}
```

**Ví dụ:**
```
http://192.168.1.100:3000/vi/tables/1?token=abc123def456ghi789
```

### Tạo QR Code Online (Khuyến nghị):

1. Truy cập: https://www.qr-code-generator.com/
2. Chọn "URL"
3. Dán URL vào
4. Click "Generate QR Code"
5. Tải về và hiển thị trên màn hình (hoặc in ra)

---

## 📲 Bước 5: Test Quét QR Code Từ Điện Thoại

### Yêu Cầu:
- ✅ Điện thoại và máy tính **cùng WiFi**
- ✅ Backend đang chạy với IP address
- ✅ Frontend đang chạy với IP address
- ✅ Đã có QR code

### Các Bước:

1. **Mở camera trên điện thoại** (iOS/Android đều có sẵn)

2. **Quét QR code:**
   - Đưa camera vào QR code
   - Tự động nhận diện và mở link

3. **Trang đăng nhập sẽ hiện ra:**
   - Số bàn đã được điền sẵn
   - Token đã được điền sẵn
   - Chỉ cần nhập **Tên khách hàng**

4. **Nhập tên và đăng nhập:**
   - Ví dụ: "Nguyễn Văn A"
   - Click "Đăng nhập"

5. **Vào trang menu:**
   - Xem danh sách món ăn
   - Click vào món để xem chi tiết
   - Thêm vào giỏ hàng
   - **Đặt món** ← Quan trọng!

---

## 👨‍💼 Bước 6: Kiểm Tra Bên Quản Lý

### 6.1. Đăng Nhập Quản Lý (Trên Máy Tính)

**Mở Terminal 3 hoặc dùng Postman:**

```bash
curl -X POST http://localhost:4000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@order.com",
    "password": "123456"
  }'
```

**Copy `accessToken`** từ response.

### 6.2. Kết Nối Socket.IO để Nhận Thông Báo Real-Time

**Cách 1: Dùng Frontend Quản Lý (Nếu có)**

- Mở trang quản lý trên trình duyệt: `http://192.168.1.100:3000/admin` (hoặc route tương ứng)
- Đăng nhập với tài khoản quản lý
- Frontend sẽ tự động kết nối Socket.IO

**Cách 2: Test Socket.IO bằng JavaScript Console**

Mở trình duyệt trên máy tính, vào trang bất kỳ, mở Console (F12) và chạy:

```javascript
// Cài đặt Socket.IO client (nếu chưa có)
// Hoặc dùng CDN: <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>

// Thay YOUR_ACCESS_TOKEN bằng token từ bước 6.1
const socket = io('http://192.168.1.100:4000', {
  auth: {
    Authorization: 'Bearer YOUR_ACCESS_TOKEN'
  }
});

socket.on('connect', () => {
  console.log('✅ Đã kết nối Socket.IO với quyền quản lý');
});

// Lắng nghe sự kiện đơn hàng mới
socket.on('new-order', (orders) => {
  console.log('📦 Đơn hàng mới:', orders);
  alert(`Có ${orders.length} đơn hàng mới từ bàn ${orders[0]?.tableNumber}`);
});

// Lắng nghe sự kiện cập nhật đơn hàng
socket.on('update-order', (order) => {
  console.log('🔄 Đơn hàng được cập nhật:', order);
});

// Lắng nghe sự kiện thanh toán
socket.on('payment', (orders) => {
  console.log('💰 Thanh toán:', orders);
  alert(`Bàn ${orders[0]?.tableNumber} đã thanh toán`);
});
```

### 6.3. Kiểm Tra Logs Backend

**Trong Terminal 1 (đang chạy backend), bạn sẽ thấy:**

```
🔌 Socket connected: abc123 (User: 1, Role: Manager)
📡 Emitted 'new-order' to manager room: [{'id': 1, 'tableNumber': 1, ...}]
```

### 6.4. Kiểm Tra API Đơn Hàng

**Xem danh sách đơn hàng:**

```bash
curl http://localhost:4000/orders/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" | python3 -m json.tool
```

**Xem đơn hàng của khách cụ thể:**

```bash
curl http://localhost:4000/orders/?guestId=1 \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" | python3 -m json.tool
```

---

## ✅ Checklist Test

### Phía Khách Hàng:
- [ ] Quét QR code thành công
- [ ] Đăng nhập được với tên khách hàng
- [ ] Xem được danh sách món ăn
- [ ] Thêm món vào giỏ hàng
- [ ] Đặt món thành công
- [ ] Xem được đơn hàng của mình

### Phía Quản Lý:
- [ ] Đăng nhập quản lý thành công
- [ ] Kết nối Socket.IO thành công
- [ ] Nhận được thông báo `new-order` khi khách đặt món
- [ ] Xem được đơn hàng mới trong danh sách
- [ ] Cập nhật trạng thái đơn hàng (nếu có chức năng)
- [ ] Nhận được thông báo `payment` khi khách thanh toán

---

## 🔧 Troubleshooting

### ❌ Không kết nối được từ điện thoại

**Nguyên nhân:**
- Không cùng WiFi
- Firewall chặn
- IP address sai

**Giải pháp:**
1. Kiểm tra cùng WiFi:
   ```bash
   # Trên máy tính
   ipconfig getifaddr en0
   
   # Trên điện thoại, vào WiFi settings
   # Xem IP của điện thoại (phải cùng subnet)
   # Ví dụ: 192.168.1.100 (máy tính) và 192.168.1.101 (điện thoại)
   ```

2. Tắt Firewall tạm thời (MacOS):
   - System Preferences → Security & Privacy → Firewall
   - Click "Turn Off Firewall" (chỉ để test)

### ❌ Quản lý không nhận được thông báo Socket.IO

**Nguyên nhân:**
- Chưa kết nối Socket.IO
- Token không hợp lệ
- Role không phải Manager

**Giải pháp:**
1. Kiểm tra token còn hợp lệ:
   ```bash
   # Đăng nhập lại để lấy token mới
   curl -X POST http://localhost:4000/auth/login ...
   ```

2. Kiểm tra logs backend:
   - Phải thấy: `🔌 Socket connected: ... (Role: Manager)`
   - Phải thấy: `📡 Emitted 'new-order' to manager room`

3. Kiểm tra role trong token:
   - Token phải có `role: "Manager"` hoặc `role: "Admin"`

### ❌ "Bàn không tồn tại hoặc mã token không đúng"

**Giải pháp:**
1. Lấy lại thông tin bàn:
   ```bash
   curl http://localhost:4000/tables/ | python3 -m json.tool
   ```

2. Tạo QR code mới với token mới

---

## 💡 Tips

### 1. Test Nhiều Khách Hàng Cùng Lúc

- Tạo QR code cho nhiều bàn khác nhau
- Mỗi điện thoại quét QR code của bàn khác nhau
- Test xem quản lý nhận được thông báo từ tất cả các bàn

### 2. Test Real-Time Updates

- Khách đặt món → Quản lý nhận thông báo ngay lập tức
- Quản lý cập nhật trạng thái đơn hàng → Khách nhận thông báo (nếu có)

### 3. Dùng ngrok để Test Từ Xa

```bash
# Cài ngrok: brew install ngrok
# Hoặc tải từ: https://ngrok.com/

# Chạy ngrok cho backend
ngrok http 4000

# Chạy ngrok cho frontend
ngrok http 3000

# Dùng URL ngrok thay vì IP local
```

---

## 🎉 Kết Quả Mong Đợi

### Khi Khách Đặt Món:
1. ✅ Khách thấy thông báo "Đặt món thành công"
2. ✅ Quản lý nhận được thông báo Socket.IO `new-order` với thông tin:
   - Số bàn
   - Tên khách hàng
   - Danh sách món đã đặt
   - Số lượng
   - Trạng thái: `Pending`
3. ✅ Đơn hàng xuất hiện trong danh sách đơn hàng của quản lý

### Khi Quản Lý Cập Nhật Đơn Hàng:
1. ✅ Quản lý cập nhật trạng thái (Processing, Delivered, etc.)
2. ✅ Khách nhận được thông báo cập nhật (nếu có Socket.IO cho khách)

---

Chúc bạn test thành công! 🚀

