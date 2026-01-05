#!/usr/bin/env python3
"""
Script to normalize all image URLs in database
Converts full URLs (production/localhost) to just filenames
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
from infrastructure.models.account_model import AccountModel
from infrastructure.models.dish_model import DishModel, DishSnapshotModel
from create_app import create_app

def normalize_image_url(image_url):
    """Extract filename from full URL"""
    if not image_url:
        return None
    
    # If it's a full URL, extract the filename
    if image_url.startswith('http://') or image_url.startswith('https://'):
        if '/static/' in image_url:
            return image_url.split('/static/')[-1]
        # If URL doesn't have /static/, try to extract last part
        return image_url.split('/')[-1]
    
    # Remove leading slash and 'static/' if exists
    normalized = image_url.lstrip('/')
    if normalized.startswith('static/'):
        normalized = normalized[7:]
    
    return normalized if normalized else None

def normalize_all_image_urls():
    """Normalize all image URLs in database"""
    print("🔄 Normalizing image URLs in database...\n")
    
    app, socketio = create_app()
    
    with app.app_context():
        session = get_session()
        try:
            updated_count = 0
            
            # Update Account avatars
            print("📝 Updating Account avatars...")
            accounts = session.query(AccountModel).all()
            for account in accounts:
                if account.avatar:
                    normalized = normalize_image_url(account.avatar)
                    if normalized != account.avatar:
                        print(f"  Account {account.id}: '{account.avatar}' -> '{normalized}'")
                        account.avatar = normalized
                        updated_count += 1
            
            # Update Dish images
            print("\n📝 Updating Dish images...")
            dishes = session.query(DishModel).all()
            for dish in dishes:
                if dish.image:
                    normalized = normalize_image_url(dish.image)
                    if normalized != dish.image:
                        print(f"  Dish {dish.id}: '{dish.image}' -> '{normalized}'")
                        dish.image = normalized
                        updated_count += 1
            
            # Update DishSnapshot images
            print("\n📝 Updating DishSnapshot images...")
            snapshots = session.query(DishSnapshotModel).all()
            for snapshot in snapshots:
                if snapshot.image:
                    normalized = normalize_image_url(snapshot.image)
                    if normalized != snapshot.image:
                        print(f"  DishSnapshot {snapshot.id}: '{snapshot.image}' -> '{normalized}'")
                        snapshot.image = normalized
                        updated_count += 1
            
            if updated_count > 0:
                session.commit()
                print(f"\n✅ Updated {updated_count} image URLs successfully!")
            else:
                print("\n✅ No URLs to update (all are already normalized)")
                
        except Exception as e:
            session.rollback()
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

if __name__ == '__main__':
    normalize_all_image_urls()

