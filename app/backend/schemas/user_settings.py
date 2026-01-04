"""User settings Pydantic schemas."""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List


class NotificationSettingsOut(BaseModel):
    """Notification settings output schema."""
    push_notifications_enabled: bool
    email_notifications_enabled: bool
    reminder_notifications_enabled: bool
    
    class Config:
        from_attributes = True


class NotificationSettingsUpdate(BaseModel):
    """Notification settings update schema."""
    push_notifications_enabled: Optional[bool] = None
    email_notifications_enabled: Optional[bool] = None
    reminder_notifications_enabled: Optional[bool] = None


class PaymentMethodOut(BaseModel):
    """Payment method output schema."""
    id: str
    user_id: str
    bank_name: str
    account_number: str
    account_holder: str
    is_default: bool
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PaymentMethodCreate(BaseModel):
    """Payment method creation schema."""
    bank_name: str = Field(..., min_length=1, max_length=50)
    account_number: str = Field(..., min_length=1, max_length=50)
    account_holder: str = Field(..., min_length=1, max_length=50)
    is_default: Optional[bool] = False


class PaymentMethodUpdate(BaseModel):
    """Payment method update schema."""
    bank_name: Optional[str] = Field(None, min_length=1, max_length=50)
    account_number: Optional[str] = Field(None, min_length=1, max_length=50)
    account_holder: Optional[str] = Field(None, min_length=1, max_length=50)
    is_default: Optional[bool] = None

