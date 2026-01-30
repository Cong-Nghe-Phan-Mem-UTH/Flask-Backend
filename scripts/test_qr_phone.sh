#!/bin/bash

# Script để test QR code từ điện thoại
# Sử dụng: ./scripts/test_qr_phone.sh

echo "🔍 Đang lấy IP address của máy tính..."
IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || hostname -I | awk '{print $1}')

if [ -z "$IP" ]; then
    echo "❌ Không tìm thấy IP address. Vui lòng nhập IP thủ công:"
    read -p "IP address: " IP
else
    echo "✅ IP address: $IP"
fi

echo ""
echo "📋 Đang lấy danh sách bàn..."
echo ""

# Lấy danh sách bàn
TABLES=$(curl -s http://localhost:4000/tables/)

if [ $? -ne 0 ]; then
    echo "❌ Không thể kết nối đến server. Đảm bảo server đang chạy tại http://localhost:4000"
    exit 1
fi

echo "$TABLES" | python3 -m json.tool 2>/dev/null || echo "$TABLES"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📱 HƯỚNG DẪN TEST TỪ ĐIỆN THOẠI"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  Đảm bảo Backend đang chạy với IP:"
echo "   cd src && DOMAIN=$IP python app.py"
echo ""
echo "2️⃣  Đảm bảo Frontend đang chạy với IP:"
echo "   cd ../NextJs-Super-FrontEnd"
echo "   npm run dev -- -H $IP"
echo ""
echo "3️⃣  Tạo QR Code với URL:"
echo "   http://$IP:3000/vi/tables/1?token=YOUR_TOKEN"
echo ""
echo "   (Thay 1 và YOUR_TOKEN bằng số bàn và token thực tế)"
echo ""
echo "4️⃣  Quét QR code bằng điện thoại (cùng WiFi)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 TẠO QR CODE ONLINE:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Truy cập: https://www.qr-code-generator.com/"
echo "Hoặc: https://qr.io/"
echo ""
echo "Dán URL vào và tải QR code về"
echo ""


