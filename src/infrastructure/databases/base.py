from sqlalchemy.orm import declarative_base
from sqlalchemy import String
from sqlalchemy.dialects.mssql import NVARCHAR
from config import Config

Base = declarative_base()

def UnicodeString(length):
    """Return NVARCHAR for MSSQL, String for other databases"""
    database_uri = Config.DATABASE_URI
    if 'mssql' in database_uri.lower():
        return NVARCHAR(length)
    return String(length)

# ORM: object relational mapping base class
# OOP : object oriented programming
# ERD --> class relational
# Lập trình hướng đối tượng (logic) mapping class -> table (database)

