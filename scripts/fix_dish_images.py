#!/usr/bin/env python3
"""
Script to fix dish images - ensure they are stored correctly in database
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
from config import Config

def normalize_image_path(image_path):
    """Normalize image path to just filename"""
    if not image_path:
        return None
    
    # If it's a full URL, extract the filename
    if image_path.startswith('http://') or image_path.startswith('https://'):
        if '/static/' in image_path:
            return image_path.split('/static/')[-1]
        return image_path.split('/')[-1]
    
    # Remove leading slash and 'static/' if exists
    normalized = image_path.lstrip('/')
    if normalized.startswith('static/'):
        normalized = normalized[7:]
    
    return normalized if normalized else None

def fix_dish_images():
    """Fix dish images in database"""
    print("🔧 Fixing dish images...\n")
    
    app, socketio = create_app()
    
    with app.app_context():
        session = get_session()
        try:
            dishes = session.query(DishModel).all()
            upload_folder = Path(Config.UPLOAD_FOLDER)
            
            print(f"📁 Upload folder: {upload_folder}\n")
            
            updated = 0
            for dish in dishes:
                if not dish.image:
                    print(f"⚠️  Dish {dish.id} ({dish.name}): No image")
                    continue
                
                # Normalize image path
                normalized = normalize_image_path(dish.image)
                
                if normalized != dish.image:
                    print(f"📝 Dish {dish.id} ({dish.name}): '{dish.image}' -> '{normalized}'")
                    dish.image = normalized
                    updated += 1
                
                # Verify file exists
                if normalized:
                    image_path = upload_folder / normalized
                    if image_path.exists():
                        print(f"  ✅ File exists: {normalized}")
                    else:
                        print(f"  ❌ File NOT found: {normalized}")
            
            if updated > 0:
                session.commit()
                print(f"\n✅ Updated {updated} dish images!")
            else:
                print("\n✅ All dish images are already normalized")
                
        except Exception as e:
            session.rollback()
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

if __name__ == '__main__':
    fix_dish_images()


