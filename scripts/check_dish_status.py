#!/usr/bin/env python3
"""
Script to check dish status in database
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

def check_dish_status():
    """Check dish status in database"""
    print("🔍 Checking dish status...\n")
    
    app, socketio = create_app()
    
    with app.app_context():
        session = get_session()
        try:
            all_dishes = session.query(DishModel).order_by(DishModel.created_at.desc()).all()
            
            print(f"📊 Total dishes: {len(all_dishes)}\n")
            
            # Group by status
            by_status = {}
            for dish in all_dishes:
                status = dish.status or 'None'
                if status not in by_status:
                    by_status[status] = []
                by_status[status].append(dish)
            
            # Print breakdown
            for status, dishes in by_status.items():
                print(f"📌 Status '{status}': {len(dishes)} món")
                for dish in dishes:
                    print(f"   - ID {dish.id}: {dish.name} (Price: {dish.price:,}đ)")
                print()
            
        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

if __name__ == '__main__':
    check_dish_status()



