import uuid
import os

def random_id():
    """Generate random ID"""
    return uuid.uuid4().hex

def create_folder(folder_path):
    """Create folder if not exists"""
    if not os.path.exists(folder_path):
        os.makedirs(folder_path, exist_ok=True)

