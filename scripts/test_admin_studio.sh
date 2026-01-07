#!/bin/bash

# Test script to check if admin_studio can be imported and run

cd "$(dirname "$0")/../src" || exit

echo "🔍 Testing Database Studio setup..."
echo ""

# Check if virtual environment is activated
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment is activated: $VIRTUAL_ENV"
else
    echo "⚠️  Virtual environment not activated"
    echo "   Run: source .venv/bin/activate"
    exit 1
fi

# Check if Flask-Admin is installed
echo "🔍 Checking Flask-Admin installation..."
python3 -c "import flask_admin" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Flask-Admin is installed"
else
    echo "❌ Flask-Admin is NOT installed"
    echo "   Run: pip install Flask-Admin>=1.6"
    exit 1
fi

# Try to import admin_studio
echo "🔍 Testing imports..."
python3 -c "
import sys
sys.path.insert(0, '.')
try:
    from admin_studio import create_admin_app
    print('✅ admin_studio imports successfully')
except Exception as e:
    print(f'❌ Error importing admin_studio: {e}')
    import traceback
    traceback.print_exc()
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All checks passed! You can now run:"
    echo "   python admin_studio.py"
else
    echo ""
    echo "❌ Some checks failed. Please fix the errors above."
    exit 1
fi

