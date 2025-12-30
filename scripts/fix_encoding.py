#!/usr/bin/env python3
"""
Script to fix encoding issues in database - re-import data with correct UTF-8 encoding
"""
import sys
import os
from pathlib import Path

# Activate venv if exists
venv_path = Path(__file__).parent.parent / 'src' / '.venv'
if venv_path.exists():
    # Add venv site-packages to path
    site_packages = venv_path / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
    if site_packages.exists():
        sys.path.insert(0, str(site_packages))

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from infrastructure.databases import get_session
from infrastructure.models.dish_model import DishModel
from create_app import create_app
import sqlite3

# Paths
NODEJS_BACKEND_DIR = Path(__file__).parent.parent.parent / 'NextJs-Super-BackEnd'
SQLITE_DB_PATH = NODEJS_BACKEND_DIR / 'prisma' / 'dev.db'

def fix_dishes():
    """Re-import dishes with correct UTF-8 encoding"""
    print("🔧 Fixing dish encoding...\n")
    
    if not SQLITE_DB_PATH.exists():
        print(f"❌ SQLite database not found: {SQLITE_DB_PATH}")
        return
    
    # Connect to SQLite with UTF-8
    sqlite_conn = sqlite3.connect(str(SQLITE_DB_PATH))
    sqlite_conn.text_factory = str  # Use str instead of bytes
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM Dish ORDER BY id")
    dishes = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    
    # Create Flask app
    app, socketio = create_app()
    
    with app.app_context():
        session = get_session()
        
        try:
            # First, delete all existing dishes to avoid duplicates
            print("🗑️  Clearing existing dishes...")
            session.query(DishModel).delete()
            session.commit()
            print("✅ Cleared existing dishes\n")
            
            # Re-import with correct encoding
            imported = 0
            for row in dishes:
                dish_dict = dict(zip(columns, row))
                
                # Ensure strings are properly decoded
                name = str(dish_dict.get('name', ''))
                description = str(dish_dict.get('description', ''))
                image = str(dish_dict.get('image', ''))
                status = str(dish_dict.get('status', 'Available'))
                
                dish = DishModel(
                    name=name,
                    price=dish_dict.get('price', 0),
                    description=description,
                    image=image,
                    status=status
                )
                session.add(dish)
                imported += 1
                print(f"  ✅ Imported: {name}")
            
            session.commit()
            print(f"\n✅ Re-imported {imported} dishes with correct UTF-8 encoding!")
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
            session.rollback()
        finally:
            session.close()
    
    sqlite_conn.close()

if __name__ == '__main__':
    fix_dishes()

