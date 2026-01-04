"""Total Manager Pydantic schemas."""
from pydantic import BaseModel, Field, field_validator
from datetime import date, datetime
from typing import Optional, List
from app.backend.db.models.total_manager import (
    GroupType,
    PaymentType,
    CollectionStatus,
    LogType,
)


# Enums (re-exported from models)
GroupTypeEnum = GroupType
PaymentTypeEnum = PaymentType
CollectionStatusEnum = CollectionStatus
LogTypeEnum = LogType


# Group schemas
class GroupCreate(BaseModel):
    """Group creation schema."""
    name: str
    type: str  # Accept string, will be validated in service layer
    
    @field_validator('type', mode='before')
    @classmethod
    def normalize_type(cls, v):
        """Normalize type to lowercase."""
        if isinstance(v, str):
            return v.lower()
        return v


class GroupOut(BaseModel):
    """Group output schema."""
    id: str
    owner_id: str
    name: str
    type: GroupType
    created_at: datetime
    
    class Config:
        from_attributes = True


class GroupUpdate(BaseModel):
    """Group update schema."""
    name: Optional[str] = None
    type: Optional[GroupType] = None


class GroupDetailOut(GroupOut):
    """Group detail output schema with statistics."""
    collections_count: int
    total_amount: int


# Collection schemas
class CollectionCreate(BaseModel):
    """Collection creation schema."""
    title: str
    amount: int
    due_date: date
    payment_type: PaymentType
    payment_value: str


class CollectionOut(BaseModel):
    """Collection output schema."""
    id: str
    group_id: str
    title: str
    amount: int
    due_date: date
    payment_type: PaymentType
    payment_value: str
    status: CollectionStatus
    created_at: datetime
    
    class Config:
        from_attributes = True


class CollectionUpdate(BaseModel):
    """Collection update schema."""
    title: Optional[str] = None
    amount: Optional[int] = None
    due_date: Optional[date] = None
    payment_type: Optional[PaymentType] = None
    payment_value: Optional[str] = None


class CollectionSummaryOut(BaseModel):
    """Collection summary output schema."""
    id: str
    title: str
    amount: int
    due_date: date
    status: CollectionStatus
    total_members: int
    read_members: int
    paid_members: int
    current_amount: int
    payment_type: PaymentType
    payment_value: str


# Member schemas
class MemberCreate(BaseModel):
    """Member creation schema."""
    display_name: str
    phone: Optional[str] = None


class MemberOut(BaseModel):
    """Member output schema."""
    id: str
    collection_id: str
    display_name: str
    phone: Optional[str]
    read_at: Optional[datetime]
    paid_at: Optional[datetime]
    created_at: datetime
    
    class Config:
        from_attributes = True


class MemberUpdate(BaseModel):
    """Member update schema."""
    display_name: Optional[str] = None
    phone: Optional[str] = None


class BulkMemberCreate(BaseModel):
    """Bulk member creation schema."""
    members: List[MemberCreate]


# Notice schemas
class NoticeCreate(BaseModel):
    """Notice creation schema."""
    message: Optional[str] = None


class NoticeOut(BaseModel):
    """Notice output schema."""
    success: bool
    message: str
    log_id: str


# Event log schemas
class EventLogOut(BaseModel):
    """Event log output schema."""
    id: str
    collection_id: str
    type: LogType
    message: str
    created_at: datetime
    
    class Config:
        from_attributes = True


# Reminder schemas
class ReminderCreate(BaseModel):
    """Reminder creation schema."""
    collection_id: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    scheduled_at: datetime
    repeat_type: str = Field(..., pattern="^(none|daily|weekly)$")
    message: Optional[str] = Field(None, max_length=500)


class ReminderUpdate(BaseModel):
    """Reminder update schema."""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    scheduled_at: Optional[datetime] = None
    repeat_type: Optional[str] = Field(None, pattern="^(none|daily|weekly)$")
    message: Optional[str] = Field(None, max_length=500)


class ReminderOut(BaseModel):
    """Reminder output schema."""
    id: str
    user_id: str
    collection_id: Optional[str]
    title: str
    scheduled_at: datetime
    repeat_type: str
    message: Optional[str]
    is_sent: bool
    sent_at: Optional[datetime]
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class LogStatsOut(BaseModel):
    """Log statistics output schema."""
    total_logs: int
    by_type: dict
    recent_activity: List[dict]

