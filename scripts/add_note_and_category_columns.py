#!/usr/bin/env python3
"""
Migration script: add `note` to Order and `category` to Dish, DishSnapshot.
Run from project root: python scripts/add_note_and_category_columns.py
Or from src with app context: cd src && python -c "
import sys
sys.path.insert(0, '.')
from scripts.add_note_and_category_columns import run; run()
"
"""
import sys
from pathlib import Path

# Allow running from project root or from scripts/
project_root = Path(__file__).resolve().parent.parent
src_path = project_root / 'src'
sys.path.insert(0, str(src_path))

import os
try:
    from dotenv import load_dotenv
    load_dotenv(src_path / '.env')
except Exception:
    pass  # ignore .env parse errors; will use default DB path

def run():
    database_uri = os.environ.get('DATABASE_URL') or 'sqlite:///dev.db'
    if 'sqlite' not in database_uri.lower():
        print('This script only supports SQLite. For PostgreSQL/MSSQL/MySQL, add columns manually.')
        return

    # SQLite: path is relative to cwd when using sqlite:///dev.db
    if database_uri.startswith('sqlite:///'):
        db_path = database_uri.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
            # dev.db is often in src/
            for base in [src_path, project_root]:
                candidate = base / db_path
                if candidate.exists():
                    db_path = str(candidate)
                    break
    else:
        print('Could not determine SQLite path.')
        return

    try:
        import sqlite3
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()

        # Order: add note (Order is reserved in SQLite, use quoted identifier)
        cur.execute('PRAGMA table_info("Order")')
        cols = [row[1] for row in cur.fetchall()]
        if 'note' not in cols:
            cur.execute('ALTER TABLE "Order" ADD COLUMN note VARCHAR(500)')
            print('Added column Order.note')
        else:
            print('Order.note already exists')

        # Dish: add category
        cur.execute('PRAGMA table_info(Dish)')
        cols = [row[1] for row in cur.fetchall()]
        if 'category' not in cols:
            cur.execute('ALTER TABLE Dish ADD COLUMN category VARCHAR(50)')
            print('Added column Dish.category')
        else:
            print('Dish.category already exists')

        # DishSnapshot: add category
        cur.execute('PRAGMA table_info(DishSnapshot)')
        cols = [row[1] for row in cur.fetchall()]
        if 'category' not in cols:
            cur.execute('ALTER TABLE DishSnapshot ADD COLUMN category VARCHAR(50)')
            print('Added column DishSnapshot.category')
        else:
            print('DishSnapshot.category already exists')

        conn.commit()
        conn.close()
        print('Migration done.')
    except Exception as e:
        print('Error:', e)
        raise

if __name__ == '__main__':
    run()
