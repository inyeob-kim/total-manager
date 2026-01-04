"""User settings database models."""
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.sql import func
from app.backend.db.base import Base


class UserSettings(Base):
    """User notification settings model."""
    __tablename__ = "user_settings"
    
    id = Column(String, primary_key=True)  # ULID string
    user_id = Column(String, unique=True, nullable=False, index=True)
    push_notifications_enabled = Column(Boolean, default=True, nullable=False)
    email_notifications_enabled = Column(Boolean, default=False, nullable=False)
    reminder_notifications_enabled = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)


class UserPaymentMethod(Base):
    """User payment method model."""
    __tablename__ = "user_payment_methods"
    
    id = Column(String, primary_key=True)  # ULID string
    user_id = Column(String, nullable=False, index=True)
    bank_name = Column(String, nullable=False)
    account_number = Column(String, nullable=False)
    account_holder = Column(String, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    __table_args__ = (
        Index('ix_user_payment_methods_user_default', 'user_id', 'is_default'),
    )

