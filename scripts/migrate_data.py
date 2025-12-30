#!/usr/bin/env python3
"""
Script to migrate data from Node.js backend (SQLite) to Flask backend (MSSQL)
"""
import sqlite3
import os
import sys
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
from infrastructure.models.account_model import AccountModel
from infrastructure.models.dish_model import DishModel, DishSnapshotModel
from infrastructure.models.table_model import TableModel
from infrastructure.models.order_model import OrderModel
from infrastructure.models.guest_model import GuestModel
from infrastructure.models.refresh_token_model import RefreshTokenModel
from infrastructure.models.socket_model import SocketModel
from config import Config
from create_app import create_app
from datetime import datetime
import shutil

# Paths
NODEJS_BACKEND_DIR = Path(__file__).parent.parent.parent / 'NextJs-Super-BackEnd'
SQLITE_DB_PATH = NODEJS_BACKEND_DIR / 'prisma' / 'dev.db'
NODEJS_UPLOADS_DIR = NODEJS_BACKEND_DIR / 'uploads'
FLASK_UPLOADS_DIR = Path(__file__).parent.parent / 'src' / 'uploads'

def copy_upload_files():
    """Copy upload files from Node.js backend to Flask backend"""
    print("📁 Copying upload files...")
    
    if not NODEJS_UPLOADS_DIR.exists():
        print(f"⚠️  Uploads directory not found: {NODEJS_UPLOADS_DIR}")
        return
    
    # Create Flask uploads directory if not exists
    FLASK_UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Copy all files
    copied = 0
    for file_path in NODEJS_UPLOADS_DIR.iterdir():
        if file_path.is_file():
            dest_path = FLASK_UPLOADS_DIR / file_path.name
            if not dest_path.exists():
                shutil.copy2(file_path, dest_path)
                copied += 1
                print(f"  ✅ Copied: {file_path.name}")
    
    print(f"✅ Copied {copied} files to Flask uploads directory\n")

def parse_datetime(dt_str):
    """Parse datetime string from SQLite"""
    if not dt_str:
        return datetime.utcnow()
    try:
        # SQLite format: 2024-01-01 12:00:00.000000 or ISO format
        if isinstance(dt_str, datetime):
            return dt_str
        if 'T' in str(dt_str):
            dt_str = str(dt_str).replace('Z', '+00:00')
            return datetime.fromisoformat(dt_str)
        else:
            # Remove microseconds if present
            dt_str = str(dt_str).split('.')[0]
            return datetime.strptime(dt_str, '%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"  ⚠️  Warning: Could not parse datetime '{dt_str}': {e}, using current time")
        return datetime.utcnow()

def migrate_accounts(sqlite_conn, flask_session):
    """Migrate Account data"""
    print("👤 Migrating Accounts...")
    
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM Account ORDER BY id")
    accounts = cursor.fetchall()
    
    # Get column names
    columns = [description[0] for description in cursor.description]
    
    migrated = 0
    id_mapping = {}  # Map old ID to new ID
    
    for row in accounts:
        account_dict = dict(zip(columns, row))
        old_id = account_dict['id']
        email = account_dict['email']
        
        # Check if account already exists
        existing = flask_session.query(AccountModel).filter_by(email=email).first()
        if existing:
            id_mapping[old_id] = existing.id
            print(f"  ⏭️  Skipped (exists): {email}")
            continue
        
        account = AccountModel(
            name=account_dict['name'],
            email=email,
            password=account_dict['password'],  # Password already hashed
            avatar=account_dict.get('avatar'),
            role=account_dict.get('role') or 'Employee',
            owner_id=None,  # Will update after all accounts are migrated
            created_at=parse_datetime(account_dict.get('createdAt')),
            updated_at=parse_datetime(account_dict.get('updatedAt'))
        )
        flask_session.add(account)
        flask_session.flush()  # Get the new ID
        id_mapping[old_id] = account.id
        migrated += 1
        print(f"  ✅ Migrated: {email} (ID: {old_id} -> {account.id})")
    
    flask_session.commit()
    
    # Update owner_id references
    print("  🔗 Updating owner relationships...")
    cursor.execute("SELECT id, ownerId FROM Account WHERE ownerId IS NOT NULL")
    owner_relations = cursor.fetchall()
    
    for old_id, old_owner_id in owner_relations:
        if old_id in id_mapping and old_owner_id in id_mapping:
            account = flask_session.query(AccountModel).get(id_mapping[old_id])
            if account:
                account.owner_id = id_mapping[old_owner_id]
    
    flask_session.commit()
    print(f"✅ Migrated {migrated} accounts\n")
    return id_mapping

def migrate_dishes(sqlite_conn, flask_session):
    """Migrate Dish data"""
    print("🍽️  Migrating Dishes...")
    
    # Set SQLite to return strings (not bytes) for UTF-8 support
    sqlite_conn.text_factory = str
    
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM Dish ORDER BY id")
    dishes = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    
    migrated = 0
    id_mapping = {}
    
    for row in dishes:
        dish_dict = dict(zip(columns, row))
        old_id = dish_dict['id']
        
        # Ensure proper string encoding
        name = str(dish_dict['name']) if dish_dict['name'] else ''
        description = str(dish_dict['description']) if dish_dict['description'] else ''
        image = str(dish_dict['image']) if dish_dict['image'] else ''
        status = str(dish_dict.get('status') or 'Available')
        
        # Check if dish already exists (by name)
        existing = flask_session.query(DishModel).filter_by(name=name).first()
        if existing:
            id_mapping[old_id] = existing.id
            # Update existing dish with correct encoding
            existing.name = name
            existing.description = description
            existing.image = image
            existing.status = status
            existing.price = dish_dict['price']
            print(f"  ✅ Updated: {name}")
            continue
        
        dish = DishModel(
            name=name,
            price=dish_dict['price'],
            description=description,
            image=image,
            status=status,
            created_at=parse_datetime(dish_dict.get('createdAt')),
            updated_at=parse_datetime(dish_dict.get('updatedAt'))
        )
        flask_session.add(dish)
        flask_session.flush()
        id_mapping[old_id] = dish.id
        migrated += 1
        print(f"  ✅ Migrated: {name} (ID: {old_id} -> {dish.id})")
    
    flask_session.commit()
    print(f"✅ Migrated {migrated} dishes\n")
    return id_mapping

def migrate_dish_snapshots(sqlite_conn, flask_session, dish_id_mapping):
    """Migrate DishSnapshot data"""
    print("📸 Migrating Dish Snapshots...")
    
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM DishSnapshot ORDER BY id")
    snapshots = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    
    migrated = 0
    id_mapping = {}
    
    for row in snapshots:
        snapshot_dict = dict(zip(columns, row))
        old_id = snapshot_dict['id']
        old_dish_id = snapshot_dict.get('dishId')
        
        # Map dish_id
        new_dish_id = dish_id_mapping.get(old_dish_id) if old_dish_id else None
        
        snapshot = DishSnapshotModel(
            name=snapshot_dict['name'],
            price=snapshot_dict['price'],
            description=snapshot_dict['description'],
            image=snapshot_dict['image'],
            status=snapshot_dict.get('status') or 'Available',
            dish_id=new_dish_id,
            created_at=parse_datetime(snapshot_dict.get('createdAt')),
            updated_at=parse_datetime(snapshot_dict.get('updatedAt'))
        )
        flask_session.add(snapshot)
        flask_session.flush()
        id_mapping[old_id] = snapshot.id
        migrated += 1
    
    flask_session.commit()
    print(f"✅ Migrated {migrated} dish snapshots\n")
    return id_mapping

def migrate_tables(sqlite_conn, flask_session):
    """Migrate Table data"""
    print("🪑 Migrating Tables...")
    
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM Table ORDER BY number")
    tables = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    
    migrated = 0
    
    for row in tables:
        table_dict = dict(zip(columns, row))
        number = table_dict['number']
        
        # Check if table already exists
        existing = flask_session.query(TableModel).filter_by(number=number).first()
        if existing:
            print(f"  ⏭️  Skipped (exists): Table {number}")
            continue
        
        table = TableModel(
            number=number,
            capacity=table_dict['capacity'],
            status=table_dict.get('status') or 'Available',
            token=table_dict['token'],
            created_at=parse_datetime(table_dict.get('createdAt')),
            updated_at=parse_datetime(table_dict.get('updatedAt'))
        )
        flask_session.add(table)
        migrated += 1
        print(f"  ✅ Migrated: Table {number}")
    
    flask_session.commit()
    print(f"✅ Migrated {migrated} tables\n")

def migrate_guests(sqlite_conn, flask_session):
    """Migrate Guest data"""
    print("👥 Migrating Guests...")
    
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM Guest ORDER BY id")
    guests = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    
    migrated = 0
    id_mapping = {}
    
    for row in guests:
        guest_dict = dict(zip(columns, row))
        old_id = guest_dict['id']
        
        guest = GuestModel(
            name=guest_dict['name'],
            table_number=guest_dict.get('tableNumber') if guest_dict.get('tableNumber') else None,
            refresh_token=guest_dict.get('refreshToken'),
            refresh_token_expires_at=parse_datetime(guest_dict.get('refreshTokenExpiresAt')) if guest_dict.get('refreshTokenExpiresAt') else None,
            created_at=parse_datetime(guest_dict.get('createdAt')),
            updated_at=parse_datetime(guest_dict.get('updatedAt'))
        )
        flask_session.add(guest)
        flask_session.flush()
        id_mapping[old_id] = guest.id
        migrated += 1
    
    flask_session.commit()
    print(f"✅ Migrated {migrated} guests\n")
    return id_mapping

def migrate_orders(sqlite_conn, flask_session, guest_id_mapping, snapshot_id_mapping, account_id_mapping):
    """Migrate Order data"""
    print("📦 Migrating Orders...")
    
    cursor = sqlite_conn.cursor()
    cursor.execute("SELECT * FROM Order ORDER BY id")
    orders = cursor.fetchall()
    columns = [description[0] for description in cursor.description]
    
    migrated = 0
    
    for row in orders:
        order_dict = dict(zip(columns, row))
        old_guest_id = order_dict.get('guestId')
        old_snapshot_id = order_dict.get('dishSnapshotId')
        old_handler_id = order_dict.get('orderHandlerId')
        
        # Map IDs
        new_guest_id = guest_id_mapping.get(old_guest_id) if old_guest_id else None
        new_snapshot_id = snapshot_id_mapping.get(old_snapshot_id) if old_snapshot_id else None
        new_handler_id = account_id_mapping.get(old_handler_id) if old_handler_id else None
        
        # Check if order already exists (by dish_snapshot_id which is unique)
        if new_snapshot_id:
            existing = flask_session.query(OrderModel).filter_by(dish_snapshot_id=new_snapshot_id).first()
            if existing:
                print(f"  ⏭️  Skipped (exists): Order with snapshot {old_snapshot_id}")
                continue
        
        order = OrderModel(
            guest_id=new_guest_id,
            table_number=order_dict.get('tableNumber') if order_dict.get('tableNumber') else None,
            dish_snapshot_id=new_snapshot_id,
            quantity=order_dict['quantity'],
            order_handler_id=new_handler_id,
            status=order_dict.get('status') or 'Pending',
            created_at=parse_datetime(order_dict.get('createdAt')),
            updated_at=parse_datetime(order_dict.get('updatedAt'))
        )
        flask_session.add(order)
        migrated += 1
    
    flask_session.commit()
    print(f"✅ Migrated {migrated} orders\n")

def main():
    """Main migration function"""
    print("🚀 Starting data migration from Node.js backend to Flask backend\n")
    
    # Check if SQLite database exists
    if not SQLITE_DB_PATH.exists():
        print(f"❌ SQLite database not found: {SQLITE_DB_PATH}")
        print("   Please make sure Node.js backend database exists.")
        return
    
    # Connect to SQLite
    print(f"📂 Connecting to SQLite database: {SQLITE_DB_PATH}")
    sqlite_conn = sqlite3.connect(SQLITE_DB_PATH)
    print("✅ Connected to SQLite\n")
    
    # Create Flask app and get session
    print("🔌 Connecting to Flask backend database...")
    app, socketio = create_app()
    
    with app.app_context():
        flask_session = get_session()
        
        try:
            # Copy upload files first
            copy_upload_files()
            
            # Migrate data in order (respecting foreign keys)
            account_id_mapping = migrate_accounts(sqlite_conn, flask_session)
            dish_id_mapping = migrate_dishes(sqlite_conn, flask_session)
            snapshot_id_mapping = migrate_dish_snapshots(sqlite_conn, flask_session, dish_id_mapping)
            migrate_tables(sqlite_conn, flask_session)
            guest_id_mapping = migrate_guests(sqlite_conn, flask_session)
            migrate_orders(sqlite_conn, flask_session, guest_id_mapping, snapshot_id_mapping, account_id_mapping)
            
            print("✨ Migration completed successfully!")
            
        except Exception as e:
            print(f"\n❌ Error during migration: {e}")
            import traceback
            traceback.print_exc()
            flask_session.rollback()
        finally:
            flask_session.close()
    
    sqlite_conn.close()
    print("\n✅ Migration process finished!")

if __name__ == '__main__':
    main()

