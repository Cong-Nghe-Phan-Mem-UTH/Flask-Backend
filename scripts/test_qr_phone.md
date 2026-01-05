# Hướng Dẫn Test QR Code Gọi Món Từ Điện Thoại

## 🎯 Mục Tiêu
Test trải nghiệm thực tế như khách hàng: quét QR code bằng điện thoại để vào trang gọi món.

---

## 📋 Bước 1: Lấy IP Address và Thông Tin Bàn

### Cách 1: Dùng Script Tự Động (Khuyến nghị)

```bash
cd /Users/mac/Documents/project_cnpm/Flask-BackEnd
chmod +x scripts/test_qr_phone.sh
./scripts/test_qr_phone.sh
```

Script sẽ tự động:
- Lấy IP address của máy tính
- Lấy danh sách bàn và token
- Hiển thị hướng dẫn chi tiết

### Cách 2: Làm Thủ Công

**1. Lấy IP address:**
```bash
ipconfig getifaddr en0
```

**2. Lấy danh sách bàn:**
```bash
curl http://localhost:4000/tables/
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

**Kiểm tra server đang chạy:**
- Mở trình duyệt: `http://192.168.1.100:4000/test/`
- Phải thấy response thành công

---

## 🎨 Bước 3: Chạy Frontend với IP Address

**Mở Terminal 2:**

```bash
cd /Users/mac/Documents/project_cnpm/NextJs-Super-FrontEnd

# Kiểm tra file .env.local hoặc .env
# Đảm bảo có:
# NEXT_PUBLIC_API_ENDPOINT=http://192.168.1.100:4000
# NEXT_PUBLIC_URL=http://192.168.1.100:3000

# Chạy với IP address
npm run dev -- -H 192.168.1.100
```

**Hoặc sửa file `.env.local`:**
```env
NEXT_PUBLIC_API_ENDPOINT=http://192.168.1.100:4000
NEXT_PUBLIC_URL=http://192.168.1.100:3000
```

Sau đó chạy:
```bash
npm run dev
```

**Kiểm tra frontend đang chạy:**
- Mở trình duyệt: `http://192.168.1.100:3000`
- Phải thấy trang chủ

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

### Tạo QR Code:

**Cách 1: Online (Khuyến nghị)**
1. Truy cập: https://www.qr-code-generator.com/
2. Chọn "URL"
3. Dán URL vào
4. Click "Generate QR Code"
5. Tải về và in ra (hoặc hiển thị trên màn hình)

**Cách 2: Dùng Python (Nếu có thư viện)**
```bash
pip install qrcode[pil]
python -c "import qrcode; qr = qrcode.QRCode(); qr.add_data('http://192.168.1.100:3000/vi/tables/1?token=abc123'); qr.make(); img = qr.make_image(); img.save('qr_code.png')"
```

**Cách 3: Dùng Terminal (MacOS)**
```bash
# Cài qrencode: brew install qrencode
echo "http://192.168.1.100:3000/vi/tables/1?token=abc123" | qrencode -o qr_code.png
```

---

## 📲 Bước 5: Test Từ Điện Thoại

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
   - Đặt món

6. **Xem đơn hàng:**
   - Vào trang "Đơn hàng của tôi"
   - Xem trạng thái đơn hàng

---

## 🔧 Troubleshooting

### ❌ Lỗi: Không kết nối được từ điện thoại

**Nguyên nhân:**
- Không cùng WiFi
- Firewall chặn
- IP address sai

**Giải pháp:**
1. **Kiểm tra cùng WiFi:**
   ```bash
   # Trên máy tính
   ipconfig getifaddr en0
   
   # Trên điện thoại, vào WiFi settings
   # Xem IP của điện thoại (phải cùng subnet)
   # Ví dụ: 192.168.1.100 (máy tính) và 192.168.1.101 (điện thoại)
   ```

2. **Tắt Firewall tạm thời (MacOS):**
   - System Preferences → Security & Privacy → Firewall
   - Click "Turn Off Firewall" (chỉ để test)

3. **Kiểm tra IP:**
   ```bash
   # Chạy lại để xác nhận IP
   ipconfig getifaddr en0
   ```

### ❌ Lỗi: "Bàn không tồn tại hoặc mã token không đúng"

**Nguyên nhân:**
- Token đã thay đổi
- Số bàn sai

**Giải pháp:**
1. Lấy lại thông tin bàn:
   ```bash
   curl http://localhost:4000/tables/
   ```

2. Tạo QR code mới với token mới

### ❌ Lỗi: Frontend không load được

**Nguyên nhân:**
- Frontend chưa chạy với IP
- Config sai

**Giải pháp:**
1. Kiểm tra frontend đang chạy:
   ```bash
   # Phải thấy output như:
   # ▲ Next.js 14.x.x
   # - Local:        http://192.168.1.100:3000
   ```

2. Kiểm tra file `.env.local`:
   ```env
   NEXT_PUBLIC_API_ENDPOINT=http://192.168.1.100:4000
   NEXT_PUBLIC_URL=http://192.168.1.100:3000
   ```

3. Restart frontend:
   ```bash
   # Dừng (Ctrl+C) và chạy lại
   npm run dev -- -H 192.168.1.100
   ```

### ❌ Lỗi: API không kết nối được

**Nguyên nhân:**
- Backend chưa chạy với IP
- CORS chưa config đúng

**Giải pháp:**
1. Kiểm tra backend đang chạy:
   ```bash
   # Phải thấy:
   # * Running on http://192.168.1.100:4000
   ```

2. Kiểm tra CORS trong `src/create_app.py`:
   ```python
   CORS(app, origins='*', supports_credentials=True)
   ```

---

## 💡 Tips

### 1. Dùng ngrok để test từ xa (không cần cùng WiFi)

```bash
# Cài ngrok: brew install ngrok
# Hoặc tải từ: https://ngrok.com/

# Chạy ngrok
ngrok http 3000

# Sẽ có URL dạng: https://abc123.ngrok.io
# Dùng URL này thay vì IP local
```

**Lưu ý:** Cần chạy ngrok cho cả backend (port 4000) và frontend (port 3000), hoặc dùng ngrok cho frontend và config frontend trỏ đến backend qua ngrok.

### 2. Tạo nhiều QR code cho nhiều bàn

```bash
# Lấy danh sách bàn
curl http://localhost:4000/tables/ | python3 -m json.tool

# Tạo QR code cho từng bàn
# Bàn 1: http://192.168.1.100:3000/vi/tables/1?token=token1
# Bàn 2: http://192.168.1.100:3000/vi/tables/2?token=token2
# ...
```

### 3. Test trên nhiều điện thoại cùng lúc

- Mỗi điện thoại quét QR code của bàn khác nhau
- Test xem có conflict không
- Test real-time updates qua Socket.IO

### 4. In QR code ra giấy

- In QR code với kích thước lớn (ít nhất 5x5cm)
- Dán lên bàn
- Test quét từ nhiều góc độ

---

## ✅ Checklist Trước Khi Test

- [ ] Backend chạy với IP address (`DOMAIN=192.168.1.100`)
- [ ] Frontend chạy với IP address (`npm run dev -- -H 192.168.1.100`)
- [ ] Đã lấy thông tin bàn (number và token)
- [ ] Đã tạo QR code với URL đúng
- [ ] Điện thoại và máy tính cùng WiFi
- [ ] Firewall đã tắt hoặc cho phép port 3000, 4000
- [ ] Đã test truy cập từ trình duyệt máy tính trước

---

## 🎉 Kết Quả Mong Đợi

Sau khi quét QR code và đăng nhập:
1. ✅ Vào được trang menu
2. ✅ Xem được danh sách món ăn
3. ✅ Thêm món vào giỏ hàng
4. ✅ Đặt món thành công
5. ✅ Xem được đơn hàng của mình
6. ✅ Real-time updates khi đơn hàng thay đổi (nếu có Socket.IO)

---

Chúc bạn test thành công! 🚀

