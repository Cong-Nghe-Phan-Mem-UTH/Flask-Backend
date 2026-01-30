#!/bin/bash
# Script to view Flask backend logs

echo "🔍 Checking Flask backend processes..."
echo ""

# Find Flask processes
FLASK_PIDS=$(ps aux | grep -E "python.*app\.py|flask.*run" | grep -v grep | awk '{print $2}')

if [ -z "$FLASK_PIDS" ]; then
    echo "❌ No Flask backend process found"
    echo ""
    echo "To start Flask backend, run:"
    echo "  cd /Users/mac/Documents/project_cnpm/Flask-BackEnd/src"
    echo "  python3 app.py"
    exit 1
fi

echo "✅ Found Flask backend process(es):"
ps aux | grep -E "python.*app\.py|flask.*run" | grep -v grep
echo ""
echo "📋 Logs will appear in the terminal where you started the backend"
echo ""
echo "💡 Tips:"
echo "  - If you started backend with 'python3 app.py', logs are in that terminal"
echo "  - Look for logs with emojis: 📄 📝 ✅ ❌ 🖼️ 📁"
echo "  - Logs include:"
echo "    • Dish creation: 📝 Creating dish with status: ..."
echo "    • Pagination: 📄 Pagination request: page=..."
echo "    • Image upload: 📤 Upload request..."
echo "    • Static files: 📁 Static request: filename=..."



