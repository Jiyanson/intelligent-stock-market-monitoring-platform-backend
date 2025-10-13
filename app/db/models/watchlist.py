# app/db/models/watchlist.py
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base_class import Base

class Watchlist(Base):
    __tablename__ = "watchlists"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    symbol = Column(String(10), nullable=False, index=True)
    company_name = Column(String(255), nullable=True)
    added_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(String(500), nullable=True)
    
    # Relationship to user
    user = relationship("User", back_populates="watchlists")
    
    # Ensure a user can't add the same symbol twice
    __table_args__ = (
        UniqueConstraint('user_id', 'symbol', name='unique_user_symbol'),
        Index('idx_user_watchlist', 'user_id', 'symbol'),
    )
    
    def __repr__(self):
        return f"<Watchlist(id={self.id}, user_id={self.user_id}, symbol={self.symbol})>"