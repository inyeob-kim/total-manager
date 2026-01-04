"""Reminders service layer."""
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from app.backend.db.models.total_manager import TMReminder, TMEventLog, LogType
from app.backend.schemas.total_manager import ReminderCreate, ReminderUpdate, ReminderOut
from app.backend.services.common import verify_collection_access
from app.backend.utils.ulid import generate_ulid


def create_reminder(
    db: Session,
    user_id: str,
    reminder_data: ReminderCreate
) -> TMReminder:
    """Create a new reminder."""
    if reminder_data.collection_id:
        verify_collection_access(db, reminder_data.collection_id, user_id)
    
    reminder = TMReminder(
        id=generate_ulid(),
        user_id=user_id,
        collection_id=reminder_data.collection_id,
        title=reminder_data.title,
        scheduled_at=reminder_data.scheduled_at,
        repeat_type=reminder_data.repeat_type,
        message=reminder_data.message,
    )
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


def list_reminders(
    db: Session,
    user_id: str,
    is_sent: Optional[bool] = None,
    collection_id: Optional[str] = None
) -> List[TMReminder]:
    """List reminders for a user."""
    query = db.query(TMReminder).filter(TMReminder.user_id == user_id)
    
    if is_sent is not None:
        query = query.filter(TMReminder.is_sent == is_sent)
    if collection_id:
        query = query.filter(TMReminder.collection_id == collection_id)
    
    return query.order_by(TMReminder.scheduled_at.asc()).all()


def get_reminder(db: Session, reminder_id: str) -> Optional[TMReminder]:
    """Get a reminder by ID."""
    return db.query(TMReminder).filter(TMReminder.id == reminder_id).first()


def verify_reminder_access(db: Session, reminder_id: str, user_id: str) -> TMReminder:
    """Verify reminder exists and belongs to user."""
    from fastapi import HTTPException, status
    
    reminder = get_reminder(db, reminder_id)
    if not reminder:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reminder not found"
        )
    if reminder.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return reminder


def update_reminder(
    db: Session,
    reminder_id: str,
    user_id: str,
    reminder_data: ReminderUpdate
) -> TMReminder:
    """Update a reminder."""
    reminder = verify_reminder_access(db, reminder_id, user_id)
    
    if reminder_data.title is not None:
        reminder.title = reminder_data.title
    if reminder_data.scheduled_at is not None:
        reminder.scheduled_at = reminder_data.scheduled_at
    if reminder_data.repeat_type is not None:
        reminder.repeat_type = reminder_data.repeat_type
    if reminder_data.message is not None:
        reminder.message = reminder_data.message
    
    db.commit()
    db.refresh(reminder)
    return reminder


def delete_reminder(db: Session, reminder_id: str, user_id: str) -> None:
    """Delete a reminder."""
    reminder = verify_reminder_access(db, reminder_id, user_id)
    db.delete(reminder)
    db.commit()


def send_reminder(db: Session, reminder_id: str, user_id: str) -> TMReminder:
    """Send a reminder immediately."""
    reminder = verify_reminder_access(db, reminder_id, user_id)
    
    reminder.is_sent = True
    reminder.sent_at = datetime.now(timezone.utc)
    
    # Create event log if collection exists
    if reminder.collection_id:
        log = TMEventLog(
            id=generate_ulid(),
            collection_id=reminder.collection_id,
            type=LogType.REMINDER_SENT,
            message=reminder.message or reminder.title,
        )
        db.add(log)
    
    # Handle repeat reminders
    if reminder.repeat_type == "daily":
        next_reminder = TMReminder(
            id=generate_ulid(),
            user_id=user_id,
            collection_id=reminder.collection_id,
            title=reminder.title,
            scheduled_at=reminder.scheduled_at + timedelta(days=1),
            repeat_type=reminder.repeat_type,
            message=reminder.message,
        )
        db.add(next_reminder)
    elif reminder.repeat_type == "weekly":
        next_reminder = TMReminder(
            id=generate_ulid(),
            user_id=user_id,
            collection_id=reminder.collection_id,
            title=reminder.title,
            scheduled_at=reminder.scheduled_at + timedelta(weeks=1),
            repeat_type=reminder.repeat_type,
            message=reminder.message,
        )
        db.add(next_reminder)
    
    db.commit()
    db.refresh(reminder)
    return reminder

