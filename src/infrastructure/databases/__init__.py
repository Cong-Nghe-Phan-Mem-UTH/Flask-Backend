from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from infrastructure.databases.base import Base
from config import Config

engine = None
SessionLocal = None

def init_db(app):
    """Initialize database"""
    global engine, SessionLocal
    
    database_uri = app.config['DATABASE_URI']
    
    # Add charset for MSSQL to support UTF-8 (Vietnamese characters)
    if 'mssql' in database_uri.lower():
        # For pymssql, add charset parameter for UTF-8 support
        if 'pymssql' in database_uri.lower():
            separator = '&' if '?' in database_uri else '?'
            if 'charset' not in database_uri.lower():
                database_uri = f"{database_uri}{separator}charset=utf8"
        # For pyodbc, ensure Unicode is used
        elif 'pyodbc' in database_uri.lower():
            separator = '&' if '?' in database_uri else '?'
            if 'charset' not in database_uri.lower():
                database_uri = f"{database_uri}{separator}charset=utf8"
    
    # For MSSQL with pymssql, we need to ensure Unicode is used
    connect_args = {}
    if 'pymssql' in database_uri.lower():
        # pymssql uses Unicode by default, no special args needed
        connect_args = {}
    elif 'mysql' in database_uri.lower():
        connect_args = {'charset': 'utf8'}
    
    # Add connection timeout for PostgreSQL
    if 'postgresql' in database_uri.lower() and 'connect_timeout' not in database_uri.lower():
        separator = '&' if '?' in database_uri else '?'
        database_uri = f"{database_uri}{separator}connect_timeout=10"
    
    engine = create_engine(
        database_uri,
        echo=app.config.get('DEBUG', False),
        pool_pre_ping=True,
        pool_recycle=300,  # Recycle connections after 5 minutes
        connect_args=connect_args
    )
    
    SessionLocal = scoped_session(
        sessionmaker(autocommit=False, autoflush=False, bind=engine)
    )
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    
    return SessionLocal

def get_session():
    """Get database session"""
    return SessionLocal()

