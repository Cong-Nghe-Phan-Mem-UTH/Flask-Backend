#!/usr/bin/env python3
"""
Script to fix UTF-8 encoding issues in existing database records
Re-encodes text fields that may have been stored incorrectly
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
from infrastructure.models.guest_model import GuestModel
from create_app import create_app

def fix_encoding(text):
    """Try to fix encoding issues"""
    if not text:
        return text
    
    # If text is already a string, try to fix common encoding issues
    if isinstance(text, str):
        # Try to detect and fix common encoding problems
        # If text contains '?' in place of Vietnamese characters, it's likely wrong encoding
        try:
            # Try to encode as latin1 then decode as utf8 (common fix)
            if '?' in text and any(ord(c) > 127 for c in text):
                # Try common encoding fixes
                try:
                    # Try cp1252 -> utf8
                    fixed = text.encode('cp1252', errors='ignore').decode('utf-8', errors='ignore')
                    if fixed != text and '?' not in fixed:
                        return fixed
                except:
                    pass
        except:
            pass
    
    return text

def fix_account_encoding():
    """Fix encoding for Account records"""
    print("🔧 Fixing Account encoding...")
    session = get_session()
    try:
        accounts = session.query(AccountModel).all()
        updated = 0
        
        for account in accounts:
            original_name = account.name
            fixed_name = fix_encoding(account.name)
            
            if fixed_name != original_name:
                print(f"  Account {account.id}: '{original_name}' -> '{fixed_name}'")
                account.name = fixed_name
                updated += 1
        
        if updated > 0:
            session.commit()
            print(f"✅ Fixed {updated} Account records\n")
        else:
            print("✅ No Account records need fixing\n")
            
    except Exception as e:
        session.rollback()
        print(f"❌ Error fixing Account encoding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

def fix_guest_encoding():
    """Fix encoding for Guest records"""
    print("🔧 Fixing Guest encoding...")
    session = get_session()
    try:
        guests = session.query(GuestModel).all()
        updated = 0
        
        for guest in guests:
            original_name = guest.name
            fixed_name = fix_encoding(guest.name)
            
            if fixed_name != original_name:
                print(f"  Guest {guest.id}: '{original_name}' -> '{fixed_name}'")
                guest.name = fixed_name
                updated += 1
        
        if updated > 0:
            session.commit()
            print(f"✅ Fixed {updated} Guest records\n")
        else:
            print("✅ No Guest records need fixing\n")
            
    except Exception as e:
        session.rollback()
        print(f"❌ Error fixing Guest encoding: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

def main():
    """Main function"""
    print("🔄 Fixing UTF-8 encoding in database...\n")
    
    app, socketio = create_app()
    
    with app.app_context():
        fix_account_encoding()
        fix_guest_encoding()
        print("✨ Encoding fix completed!")

if __name__ == '__main__':
    main()



