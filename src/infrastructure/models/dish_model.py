from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from infrastructure.databases.base import Base, UnicodeString
from datetime import datetime

class DishModel(Base):
    __tablename__ = 'Dish'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Use UnicodeString (NVARCHAR for MSSQL) to support Vietnamese characters
    name = Column(UnicodeString(255), nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(UnicodeString(1000), nullable=False)
    image = Column(UnicodeString(500), nullable=False)
    status = Column(UnicodeString(50), default='Available')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    dish_snapshots = relationship('DishSnapshotModel', backref='dish', lazy=True, cascade='all, delete-orphan')
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'image': self.image,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

class DishSnapshotModel(Base):
    __tablename__ = 'DishSnapshot'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    # Use UnicodeString (NVARCHAR for MSSQL) to support Vietnamese characters
    name = Column(UnicodeString(255), nullable=False)
    price = Column(Integer, nullable=False)
    description = Column(UnicodeString(1000), nullable=False)
    image = Column(UnicodeString(500), nullable=False)
    status = Column(UnicodeString(50), default='Available')
    dish_id = Column(Integer, ForeignKey('Dish.id'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    order = relationship('OrderModel', backref='dish_snapshot', uselist=False, lazy=True)
    
    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'price': self.price,
            'description': self.description,
            'image': self.image,
            'status': self.status,
            'dishId': self.dish_id,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

