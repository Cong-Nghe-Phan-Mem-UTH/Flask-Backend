#!/usr/bin/env python3
"""
Script to recreate tables with NVARCHAR for MSSQL
"""
import sys
from pathlib import Path

# Activate venv if exists
venv_path = Path(__file__).parent.parent / 'src' / '.venv'
if venv_path.exists():
    site_packages = venv_path / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
    if site_packages.exists():
        sys.path.insert(0, str(site_packages))

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from infrastructure.databases import get_session
from infrastructure.databases.base import Base
from infrastructure.databases import init_db
from create_app import create_app

def recreate_tables():
    """Drop and recreate all tables"""
    print("🔄 Recreating tables with NVARCHAR support...\n")
    
    app, socketio = create_app()
    
    with app.app_context():
        try:
            from infrastructure.databases import engine
            
            # Drop all tables
            print("🗑️  Dropping existing tables...")
            Base.metadata.drop_all(bind=engine)
            print("✅ Tables dropped\n")
            
            # Create tables with new schema (NVARCHAR)
            print("🔨 Creating tables with NVARCHAR...")
            Base.metadata.create_all(bind=engine)
            print("✅ Tables created with NVARCHAR support!\n")
            
            print("✨ Now run fix_encoding.py to re-import data with correct encoding")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    recreate_tables()

