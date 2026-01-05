#!/usr/bin/env python3
"""
Script to check dish images in database and verify files exist
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

def check_dish_images():
    """Check dish images in database"""
    print("🔍 Checking dish images...\n")
    
    app, socketio = create_app()
    
    with app.app_context():
        session = get_session()
        try:
            dishes = session.query(DishModel).all()
            upload_folder = Path(Config.UPLOAD_FOLDER)
            
            print(f"📁 Upload folder: {upload_folder}\n")
            
            for dish in dishes:
                print(f"Dish ID {dish.id}: {dish.name}")
                print(f"  Image in DB: '{dish.image}'")
                
                if dish.image:
                    # Check if file exists
                    image_path = upload_folder / dish.image
                    if image_path.exists():
                        print(f"  ✅ File exists: {image_path}")
                        # Format URL
                        config = Config()
                        api_url = config.API_URL
                        full_url = f"{api_url}/static/{dish.image}"
                        print(f"  🔗 Full URL: {full_url}")
                    else:
                        print(f"  ❌ File NOT found: {image_path}")
                else:
                    print(f"  ⚠️  No image in database")
                print()
                
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

if __name__ == '__main__':
    check_dish_images()


