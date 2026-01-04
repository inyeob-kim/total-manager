"""Total Manager database models."""
from sqlalchemy import Column, String, Integer, Date, DateTime, Boolean, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.backend.db.base import Base
import enum


class GroupType(str, enum.Enum):
    """Group type enumeration."""
    PARENTS = "parents"
    CLUB = "club"
    STUDY = "study"
    OTHER = "other"


class PaymentType(str, enum.Enum):
    """Payment type enumeration."""
    BANK = "bank"
    LINK = "link"


class CollectionStatus(str, enum.Enum):
    """Collection status enumeration."""
    ACTIVE = "active"
    DUE_SOON = "due_soon"
    CLOSED = "closed"


class LogType(str, enum.Enum):
    """Event log type enumeration."""
    NOTICE_SENT = "notice_sent"
    READ = "read"
    PAID_MARKED = "paid_marked"
    REMINDER_SCHEDULED = "reminder_scheduled"
    REMINDER_SENT = "reminder_sent"


class TMGroup(Base):
    """Total Manager Group model."""
    __tablename__ = "tm_groups"
    
    id = Column(String, primary_key=True)  # ULID string
    owner_id = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    type = Column(String(20), nullable=False)  # Store as plain string instead of enum
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    collections = relationship("TMCollection", back_populates="group", cascade="all, delete-orphan")


class TMCollection(Base):
    """Total Manager Collection model."""
    __tablename__ = "tm_collections"
    
    id = Column(String, primary_key=True)  # ULID string
    group_id = Column(String, ForeignKey("tm_groups.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String, nullable=False)
    amount = Column(Integer, nullable=False)
    due_date = Column(Date, nullable=False)
    payment_type = Column(String(20), nullable=False)  # Store as plain string instead of enum
    payment_value = Column(String, nullable=False)
    status = Column(String(20), nullable=False, default='active')  # Store as plain string instead of enum
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    group = relationship("TMGroup", back_populates="collections")
    members = relationship("TMMemberStatus", back_populates="collection", cascade="all, delete-orphan")
    logs = relationship("TMEventLog", back_populates="collection", cascade="all, delete-orphan")


class TMMemberStatus(Base):
    """Total Manager Member Status model."""
    __tablename__ = "tm_member_status"
    
    id = Column(String, primary_key=True)  # ULID string
    collection_id = Column(String, ForeignKey("tm_collections.id", ondelete="CASCADE"), nullable=False, index=True)
    display_name = Column(String, nullable=False)
    phone = Column(String, nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    paid_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    collection = relationship("TMCollection", back_populates="members")


class TMEventLog(Base):
    """Total Manager Event Log model."""
    __tablename__ = "tm_event_logs"
    
    id = Column(String, primary_key=True)  # ULID string
    collection_id = Column(String, ForeignKey("tm_collections.id", ondelete="CASCADE"), nullable=False)
    type = Column(SQLEnum(LogType), nullable=False)
    message = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    collection = relationship("TMCollection", back_populates="logs")

    __table_args__ = (
        Index('ix_tm_event_logs_collection_created', 'collection_id', 'created_at', postgresql_ops={'created_at': 'DESC'}),
    )


class TMReminder(Base):
    """Total Manager Reminder model."""
    __tablename__ = "tm_reminders"
    
    id = Column(String, primary_key=True)  # ULID string
    user_id = Column(String, nullable=False, index=True)
    collection_id = Column(String, ForeignKey("tm_collections.id", ondelete="SET NULL"), nullable=True)
    title = Column(String, nullable=False)
    scheduled_at = Column(DateTime(timezone=True), nullable=False, index=True)
    repeat_type = Column(String, nullable=False)  # "none", "daily", "weekly"
    message = Column(String, nullable=True)
    is_sent = Column(Boolean, default=False, nullable=False)
    sent_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), onupdate=func.now(), nullable=True)
    
    collection = relationship("TMCollection", foreign_keys=[collection_id])

    __table_args__ = (
        Index('ix_tm_reminders_user_scheduled', 'user_id', 'scheduled_at'),
        Index('ix_tm_reminders_user_sent', 'user_id', 'is_sent'),
    )

