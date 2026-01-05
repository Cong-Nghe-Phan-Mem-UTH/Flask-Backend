from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base, UnicodeString
from datetime import datetime

class GuestModel(Base):
    __tablename__ = 'Guest'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Use UnicodeString (NVARCHAR for MSSQL) to support Vietnamese characters
    name = Column(UnicodeString(255), nullable=False)
    table_number = Column(Integer, ForeignKey('Table.number'), nullable=True)
    refresh_token = Column(String(500), nullable=True)
    refresh_token_expires_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = relationship('OrderModel', backref='guest', lazy=True)
    sockets = relationship('SocketModel', backref='guest', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'tableNumber': self.table_number,
            'role': 'Guest',
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

