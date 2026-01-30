#!/usr/bin/env python3
"""
Script to restore only 4 old dishes (remove new dishes and add back old ones)
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

# Set .env path before importing config
import os
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / 'src' / '.env'
if env_path.exists():
    load_dotenv(dotenv_path=env_path)

from infrastructure.databases import get_session
from infrastructure.models.dish_model import DishModel
from create_app import create_app

# 4 món ăn cũ (trước khi recreate tables)
OLD_DISHES = [
    {
        'name': 'Phở Bò',
        'price': 50000,
        'description': 'Phở bò truyền thống với nước dùng đậm đà, thịt bò tái, bánh phở mềm',
        'image': '2356c8eb05b04c9285305b6b23bfd25c.jpg',
        'status': 'Available'
    },
    {
        'name': 'Bún Chả',
        'price': 45000,
        'description': 'Bún chả Hà Nội với thịt nướng thơm lừng, nước mắm chua ngọt đậm đà',
        'image': '2a3046651a6d4bd4aca4c82d52a0b7ec.jpg',
        'status': 'Available'
    },
    {
        'name': 'Bánh Mì',
        'price': 25000,
        'description': 'Bánh mì Việt Nam với pate, thịt nguội, chả lụa, rau củ tươi ngon',
        'image': '9d2cbde8ef0d49bcbd485bebedfeba36.jpg',
        'status': 'Available'
    },
    {
        'name': 'Cơm Tấm',
        'price': 40000,
        'description': 'Cơm tấm Sài Gòn với sườn nướng, bì, chả trứng, đồ chua',
        'image': 'd34647fadcde4b9c9bc66473ec71327d.jpg',
        'status': 'Available'
    }
]

def restore_old_dishes():
    """Remove all dishes and restore only 4 old dishes"""
    print("🔄 Restoring 4 old dishes...\n")
    
    app, socketio = create_app()
    
    with app.app_context():
        session = get_session()
        try:
            # Get existing dishes
            existing_dishes = session.query(DishModel).all()
            existing_names = {dish.name for dish in existing_dishes}
            
            # Delete all existing dishes
            if existing_dishes:
                print(f"🗑️  Deleting {len(existing_dishes)} existing dishes...")
                for dish in existing_dishes:
                    session.delete(dish)
                session.commit()
                print("✅ Deleted all existing dishes\n")
            
            # Add 4 old dishes
            print("➕ Adding 4 old dishes...")
            added = 0
            for dish_data in OLD_DISHES:
                dish = DishModel(
                    name=dish_data['name'],
                    price=dish_data['price'],
                    description=dish_data['description'],
                    image=dish_data['image'],
                    status=dish_data['status']
                )
                session.add(dish)
                added += 1
                print(f"  ✅ Added: {dish_data['name']} - {dish_data['price']:,}đ (image: {dish_data['image']})")
            
            session.commit()
            print(f"\n✅ Successfully restored {added} old dishes!")
                
        except Exception as e:
            session.rollback()
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

if __name__ == '__main__':
    restore_old_dishes()



