"""Reminders router."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List, Optional

from app.backend.db.session import get_db
from app.backend.schemas.total_manager import (
    ReminderCreate,
    ReminderUpdate,
    ReminderOut,
)
from app.backend.services.reminders_service import (
    create_reminder,
    list_reminders,
    get_reminder,
    update_reminder,
    delete_reminder,
    send_reminder,
    verify_reminder_access,
)

router = APIRouter(prefix="/total-manager/reminders", tags=["reminders"])


# Temporary auth dependency - replace with actual auth when available
def get_current_user_id() -> str:
    """Get current user ID. TODO: Replace with actual auth."""
    return "user_123"


@router.post("", response_model=ReminderOut, status_code=status.HTTP_201_CREATED)
def create_reminder_endpoint(
    reminder_data: ReminderCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Create a new reminder."""
    return create_reminder(db, user_id, reminder_data)


@router.get("", response_model=List[ReminderOut])
def list_reminders_endpoint(
    is_sent: Optional[bool] = None,
    collection_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List reminders for the current user."""
    return list_reminders(db, user_id, is_sent=is_sent, collection_id=collection_id)


@router.get("/{reminder_id}", response_model=ReminderOut)
def get_reminder_endpoint(
    reminder_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get a reminder by ID."""
    return verify_reminder_access(db, reminder_id, user_id)


@router.patch("/{reminder_id}", response_model=ReminderOut)
def update_reminder_endpoint(
    reminder_id: str,
    reminder_data: ReminderUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update a reminder."""
    return update_reminder(db, reminder_id, user_id, reminder_data)


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder_endpoint(
    reminder_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Delete a reminder."""
    delete_reminder(db, reminder_id, user_id)
    return None


@router.post("/{reminder_id}/send", response_model=ReminderOut)
def send_reminder_endpoint(
    reminder_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Send a reminder immediately."""
    return send_reminder(db, reminder_id, user_id)

