from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from infrastructure.databases.base import Base
from datetime import datetime

class RefreshTokenModel(Base):
    __tablename__ = 'RefreshToken'
    __table_args__ = {'extend_existing': True}

    token = Column(String(500), primary_key=True)
    account_id = Column(Integer, ForeignKey('Account.id', ondelete='CASCADE'), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        return {
            'token': self.token,
            'accountId': self.account_id,
            'expiresAt': self.expires_at.isoformat() if self.expires_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None
        }

