from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base
from datetime import datetime

class TableModel(Base):
    __tablename__ = 'Table'
    __table_args__ = {'extend_existing': True}

    number = Column(Integer, primary_key=True)
    capacity = Column(Integer, nullable=False)
    status = Column(String(50), default='Available')
    token = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    orders = relationship('OrderModel', backref='table', lazy=True)
    guests = relationship('GuestModel', backref='table', lazy=True)
    
    def to_dict(self):
        return {
            'number': self.number,
            'capacity': self.capacity,
            'status': self.status,
            'token': self.token,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

