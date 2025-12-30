from sqlalchemy import Column, String, Integer, ForeignKey
from infrastructure.databases.base import Base

class SocketModel(Base):
    __tablename__ = 'Socket'
    __table_args__ = {'extend_existing': True}

    socket_id = Column(String(255), primary_key=True)
    account_id = Column(Integer, ForeignKey('Account.id'), unique=True, nullable=True)
    guest_id = Column(Integer, ForeignKey('Guest.id'), unique=True, nullable=True)
    
    def to_dict(self):
        return {
            'socketId': self.socket_id,
            'accountId': self.account_id,
            'guestId': self.guest_id
        }

