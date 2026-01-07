# Sửa lỗi "Failed to open/read local data from file/application"

## Nguyên nhân:

Lỗi này xảy ra khi:

1. Đường dẫn file không đúng
2. File không tồn tại
3. Không có quyền đọc file

## Cách sửa:

### Bước 1: Kiểm tra file có tồn tại không

**Trong Terminal, chạy:**

```bash
# Kiểm tra file có tồn tại không
ls -la /Users/mac/Desktop/test.jpg

# Hoặc nếu bạn không biết đường dẫn, tìm file ảnh
find ~/Desktop -name "*.jpg" -o -name "*.png" | head -5
```

### Bước 2: Lấy đường dẫn chính xác

**Cách 1: Kéo thả file vào Terminal**

1. Mở Terminal
2. Gõ: `curl -X POST http://localhost:4000/media/test -F "file=@`
3. **Kéo file ảnh từ Finder vào Terminal** (sau dấu @)
4. Terminal sẽ tự động điền đường dẫn
5. Hoàn thành lệnh: `"`

**Cách 2: Copy đường dẫn từ Finder**

1. Mở Finder
2. Tìm file ảnh
3. **Click chuột phải** vào file → **Option + Click** (hoặc giữ Option) → Chọn **"Copy ... as Pathname"**
4. Dán vào lệnh curl

**Cách 3: Dùng đường dẫn tương đối**

```bash
# Nếu file ở Desktop
curl -X POST http://localhost:4000/media/test \
  -F "file=@~/Desktop/test.jpg"

# Nếu file ở Documents
curl -X POST http://localhost:4000/media/test \
  -F "file=@~/Documents/test.jpg"
```

### Bước 3: Test với đường dẫn đúng

**Ví dụ với file thật:**

```bash
# Tìm file ảnh trên Desktop
ls ~/Desktop/*.jpg ~/Desktop/*.png 2>/dev/null | head -1

# Copy đường dẫn từ kết quả trên, rồi dùng:
curl -X POST http://localhost:4000/media/test \
  -F "file=@/Users/mac/Desktop/your-image.jpg"
```

---

## Cách dễ nhất: Dùng Postman

Nếu gặp khó khăn với đường dẫn, **dùng Postman** sẽ dễ hơn:

1. **Mở Postman**
2. **Method:** POST
3. **URL:** `http://localhost:4000/media/test`
4. **Body** → Chọn **form-data**
5. **Key:** `file` (chọn type là **File**)
6. **Value:** Click **Select Files** → Chọn file ảnh từ Finder
7. Click **Send**

Không cần gõ đường dẫn, chỉ cần click chọn file!

---

## Test nhanh với file có sẵn

Nếu bạn có file ảnh trong project:

```bash
# Kiểm tra file có sẵn trong thư mục uploads
ls /Users/mac/Documents/project_cnpm/Flask-BackEnd/src/uploads/*.jpg | head -1

# Nếu có, dùng file đó để test
curl -X POST http://localhost:4000/media/test \
  -F "file=@/Users/mac/Documents/project_cnpm/Flask-BackEnd/src/uploads/your-file.jpg"
```

---

## Tạo file test nhanh (nếu không có ảnh)

Nếu bạn không có file ảnh để test, có thể tải một file test:

```bash
# Tải file test từ internet
curl -o ~/Desktop/test.jpg https://via.placeholder.com/300.jpg

# Sau đó test upload
curl -X POST http://localhost:4000/media/test \
  -F "file=@~/Desktop/test.jpg"
```

---

## Kiểm tra quyền file

Nếu vẫn lỗi, kiểm tra quyền:

```bash
# Xem quyền file
ls -l /path/to/your/file.jpg

# Nếu không có quyền đọc, thêm quyền
chmod 644 /path/to/your/file.jpg
```
