#!/bin/bash

# Script nhanh để fix lỗi localhost trên điện thoại
# Sử dụng: ./scripts/fix_localhost_phone.sh

echo "🔧 FIX LỖI: Không thể truy cập localhost từ điện thoại"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Lấy IP address
echo "📡 Đang lấy IP address..."
IP=$(ifconfig | grep "inet " | grep -v 127.0.0.1 | awk '{print $2}' | head -1)

if [ -z "$IP" ]; then
    echo "❌ Không tìm thấy IP. Thử cách khác..."
    IP=$(ipconfig getifaddr en0 2>/dev/null)
fi

if [ -z "$IP" ]; then
    echo "❌ Không tìm thấy IP tự động."
    echo "Vui lòng kiểm tra thủ công:"
    echo "  1. Mở System Preferences → Network"
    echo "  2. Xem IP address (thường là 192.168.x.x hoặc 10.0.x.x)"
    echo ""
    read -p "Nhập IP address của máy tính: " IP
else
    echo "✅ Tìm thấy IP: $IP"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 CÁC BƯỚC ĐỂ FIX:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "1️⃣  DỪNG Frontend hiện tại (nếu đang chạy):"
echo "   Nhấn Ctrl+C trong terminal đang chạy frontend"
echo ""
echo "2️⃣  CHẠY LẠI Frontend với IP address:"
echo ""
echo "   cd /Users/mac/Documents/project_cnpm/NextJs-Super-FrontEnd"
echo "   npm run dev -- -H $IP"
echo ""
echo "   ⚠️  QUAN TRỌNG: Phải có flag -H $IP"
echo ""
echo "3️⃣  KIỂM TRA Frontend đang chạy:"
echo "   Mở trình duyệt trên máy tính:"
echo "   http://$IP:3000"
echo "   (Phải thấy trang web, không phải lỗi)"
echo ""
echo "4️⃣  TRUY CẬP TỪ ĐIỆN THOẠI:"
echo "   Mở trình duyệt trên điện thoại (cùng WiFi):"
echo "   http://$IP:3000"
echo ""
echo "   ⚠️  KHÔNG dùng localhost:3000"
echo ""
echo "5️⃣  TẠO QR CODE MỚI:"
echo "   URL: http://$IP:3000/vi/tables/1?token=YOUR_TOKEN"
echo "   (Thay 1 và YOUR_TOKEN bằng thông tin thực tế)"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 KIỂM TRA THÊM:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Điện thoại và máy tính phải CÙNG WiFi"
echo "✅ Firewall có thể cần tắt tạm thời"
echo "✅ IP phải là IP local (192.168.x.x hoặc 10.0.x.x)"
echo ""
echo "Nếu vẫn lỗi, kiểm tra:"
echo "  - Firewall: System Preferences → Security → Firewall"
echo "  - WiFi: Đảm bảo cùng mạng"
echo "  - IP: Chạy lại script này để xác nhận IP"
echo ""

