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
    database_uri = (os.environ.get('DATABASE_URL') or 'sqlite:///dev.db').strip()
    # Render often gives postgres://; psycopg2 expects postgresql://
    if database_uri.startswith('postgres://'):
        database_uri = 'postgresql://' + database_uri[9:]

    # PostgreSQL (e.g. Render)
    if 'postgresql' in database_uri.lower():
        try:
            import psycopg2
            from urllib.parse import urlparse
            parsed = urlparse(database_uri)
            conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port or 5432,
                dbname=parsed.path.lstrip('/'),
                user=parsed.username,
                password=parsed.password,
                sslmode='require' if 'render.com' in (parsed.hostname or '') else None
            )
            cur = conn.cursor()
            # Order
            cur.execute('ALTER TABLE "Order" ADD COLUMN IF NOT EXISTS note VARCHAR(500)')
            print('Order.note: OK')
            cur.execute('ALTER TABLE "Dish" ADD COLUMN IF NOT EXISTS category VARCHAR(50)')
            print('Dish.category: OK')
            cur.execute('ALTER TABLE "DishSnapshot" ADD COLUMN IF NOT EXISTS category VARCHAR(50)')
            print('DishSnapshot.category: OK')
            conn.commit()
            cur.close()
            conn.close()
            print('PostgreSQL migration done.')
            return
        except Exception as e:
            print('PostgreSQL migration error:', e)
            raise

    if 'sqlite' not in database_uri.lower():
        print('This script supports SQLite and PostgreSQL. For MSSQL/MySQL, add columns manually.')
        return

    # SQLite
    if database_uri.startswith('sqlite:///'):
        db_path = database_uri.replace('sqlite:///', '')
        if not os.path.isabs(db_path):
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

        cur.execute('PRAGMA table_info("Order")')
        cols = [row[1] for row in cur.fetchall()]
        if 'note' not in cols:
            cur.execute('ALTER TABLE "Order" ADD COLUMN note VARCHAR(500)')
            print('Added column Order.note')
        else:
            print('Order.note already exists')

        cur.execute('PRAGMA table_info(Dish)')
        cols = [row[1] for row in cur.fetchall()]
        if 'category' not in cols:
            cur.execute('ALTER TABLE Dish ADD COLUMN category VARCHAR(50)')
            print('Added column Dish.category')
        else:
            print('Dish.category already exists')

        cur.execute('PRAGMA table_info(DishSnapshot)')
        cols = [row[1] for row in cur.fetchall()]
        if 'category' not in cols:
            cur.execute('ALTER TABLE DishSnapshot ADD COLUMN category VARCHAR(50)')
            print('Added column DishSnapshot.category')
        else:
            print('DishSnapshot.category already exists')

        conn.commit()
        conn.close()
        print('SQLite migration done.')
    except Exception as e:
        print('Error:', e)
        raise

if __name__ == '__main__':
    run()
