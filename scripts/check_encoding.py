#!/usr/bin/env python3
"""
Script to check encoding of data in database
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
from infrastructure.models.dish_model import DishModel
from create_app import create_app

def check_encoding():
    """Check encoding of dishes in database"""
    print("🔍 Checking dish encoding in database...\n")
    
    app, socketio = create_app()
    
    with app.app_context():
        session = get_session()
        
        try:
            dishes = session.query(DishModel).all()
            
            print(f"Found {len(dishes)} dishes:\n")
            for dish in dishes:
                print(f"ID: {dish.id}")
                print(f"  Name: {dish.name}")
                print(f"  Name (repr): {repr(dish.name)}")
                print(f"  Description: {dish.description[:50]}...")
                print(f"  Description (repr): {repr(dish.description[:50])}")
                print()
            
            # Check if there are encoding issues
            has_issues = False
            for dish in dishes:
                if '?' in dish.name or '?' in dish.description:
                    has_issues = True
                    print(f"⚠️  Encoding issue found in dish ID {dish.id}: {dish.name}")
            
            if not has_issues:
                print("✅ No encoding issues found in database!")
            else:
                print("\n❌ Encoding issues detected. Need to re-import data.")
                
        except Exception as e:
            print(f"❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

if __name__ == '__main__':
    check_encoding()


