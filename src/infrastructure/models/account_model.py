from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base, UnicodeString
from datetime import datetime

class AccountModel(Base):
    __tablename__ = 'Account'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Use UnicodeString (NVARCHAR for MSSQL) to support Vietnamese characters
    name = Column(UnicodeString(255), nullable=False)
    email = Column(UnicodeString(255), unique=True, nullable=False)
    password = Column(String(255), nullable=False)  # Password doesn't need Unicode
    avatar = Column(UnicodeString(500), nullable=True)
    role = Column(UnicodeString(50), default='Employee')  # Owner, Employee
    owner_id = Column(Integer, ForeignKey('Account.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    owner = relationship('AccountModel', remote_side=[id], backref='employees')
    orders = relationship('OrderModel', backref='order_handler_account', lazy=True)
    refresh_tokens = relationship('RefreshTokenModel', backref='account', lazy=True, cascade='all, delete-orphan')
    sockets = relationship('SocketModel', backref='account', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'avatar': self.avatar,
            'role': self.role,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

