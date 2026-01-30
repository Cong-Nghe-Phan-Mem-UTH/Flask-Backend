#!/usr/bin/env python3
"""
Script to set category (main, side, drink) for existing dishes based on name/description.
Run from project root: python3 scripts/set_dish_categories.py
Or with venv: source src/.venv/bin/activate && python scripts/set_dish_categories.py
"""
import sys
import re
from pathlib import Path

venv_path = Path(__file__).parent.parent / 'src' / '.venv'
if venv_path.exists():
    site_packages = venv_path / 'lib' / f'python{sys.version_info.major}.{sys.version_info.minor}' / 'site-packages'
    if site_packages.exists():
        sys.path.insert(0, str(site_packages))

sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

import os
from dotenv import load_dotenv
env_path = Path(__file__).parent.parent / 'src' / '.env'
if env_path.exists():
    try:
        load_dotenv(dotenv_path=env_path)
    except Exception:
        pass

from infrastructure.databases import get_session
from infrastructure.models.dish_model import DishModel
from create_app import create_app

# Keywords for classification (lowercase, will match name + description)
DRINK_KEYWORDS = [
    'nước', 'nuoc', 'pepsi', 'coca', 'cola', 'aqua', 'lavie', 'khoáng', 'khoang',
    'cafe', 'cà phê', 'ca phe', 'trà', 'tra', 'tea', 'soda', 'bia', 'beer',
    'drink', 'đồ uống', 'do uong', 'sinh tố', 'sinh to', 'smoothie', 'juice',
    'chè', 'che ', 'sữa', 'sua', 'milk', '0 calo', 'zero calo', 'mineral'
]
SIDE_KEYWORDS = [
    'khoai tây chiên', 'khoai tay chien', 'french fries', 'fries',
    'salad', 'đồ chua', 'do chua', 'pickle', 'rau củ', 'rau cu',
    'ăn kèm', 'an kem', 'side', 'phụ', 'phu'
]

def normalize(s):
    """Remove accents for matching (simple)."""
    if not s:
        return ''
    s = s.lower().strip()
    # Keep Vietnamese as-is for keyword match; also allow simple ascii
    return s

def classify_dish(name, description):
    """
    Return 'drink', 'side', or 'main' based on name and description.
    """
    text = f"{name or ''} {description or ''}".lower()
    # Remove extra spaces
    text = re.sub(r'\s+', ' ', text)

    for kw in DRINK_KEYWORDS:
        if kw in text:
            return 'drink'
    for kw in SIDE_KEYWORDS:
        if kw in text:
            return 'side'
    # Default: main (phở, bún, cơm, bánh mì, hamburger, etc.)
    return 'main'

def run():
    print("🍽️  Setting dish categories (main / side / drink)...\n")

    app, socketio = create_app()
    with app.app_context():
        session = get_session()
        try:
            dishes = session.query(DishModel).order_by(DishModel.id).all()
            if not dishes:
                print("  No dishes in database.")
                return

            for dish in dishes:
                name = dish.name or ''
                desc = (dish.description or '')[:500]
                new_cat = classify_dish(name, desc)
                dish.category = new_cat
                print(f"  ✅ ID {dish.id}: {name[:50]} -> {new_cat}")

            session.commit()
            print(f"\n✅ Đã gán category cho {len(dishes)} món (main / side / drink).")
        except Exception as e:
            session.rollback()
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            session.close()

if __name__ == '__main__':
    run()
