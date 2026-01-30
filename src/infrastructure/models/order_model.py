from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from infrastructure.databases.base import Base, UnicodeString
from datetime import datetime

class OrderModel(Base):
    __tablename__ = 'Order'
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, autoincrement=True)
    guest_id = Column(Integer, ForeignKey('Guest.id'), nullable=True)
    table_number = Column(Integer, ForeignKey('Table.number'), nullable=True)
    dish_snapshot_id = Column(Integer, ForeignKey('DishSnapshot.id'), unique=True, nullable=False)
    quantity = Column(Integer, nullable=False)
    note = Column(UnicodeString(500), nullable=True)  # Ghi chú cho món (guest/manager)
    order_handler_id = Column(Integer, ForeignKey('Account.id'), nullable=True)
    status = Column(String(50), default='Pending')
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        return {
            'id': self.id,
            'guestId': self.guest_id,
            'tableNumber': self.table_number,
            'dishSnapshotId': self.dish_snapshot_id,
            'quantity': self.quantity,
            'note': self.note,
            'orderHandlerId': self.order_handler_id,
            'status': self.status,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None
        }

