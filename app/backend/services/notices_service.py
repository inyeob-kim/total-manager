"""Notices service layer."""
from sqlalchemy.orm import Session
from datetime import timedelta

from app.backend.db.models.total_manager import TMEventLog, LogType
from app.backend.schemas.total_manager import NoticeCreate, NoticeOut
from app.backend.services.common import verify_collection_access
from app.backend.utils.ulid import generate_ulid


def send_notice(
    db: Session,
    collection_id: str,
    owner_id: str,
    notice_data: NoticeCreate
) -> NoticeOut:
    """Send a notice and create reminder logs."""
    from app.backend.db.models.total_manager import TMCollection
    collection = verify_collection_access(db, collection_id, owner_id)
    
    # Generate default message if not provided
    message = notice_data.message or f"'{collection.title}' 모금 안내: {collection.amount:,}원, 마감일: {collection.due_date}"
    
    # Create notice_sent log
    notice_log = TMEventLog(
        id=generate_ulid(),
        collection_id=collection_id,
        type=LogType.NOTICE_SENT,
        message=message,
    )
    db.add(notice_log)
    
    # Create reminder_scheduled logs for due_date - 1 day and due_date + 1 day
    reminder_dates = [
        collection.due_date - timedelta(days=1),
        collection.due_date + timedelta(days=1),
    ]
    
    for reminder_date in reminder_dates:
        reminder_log = TMEventLog(
            id=generate_ulid(),
            collection_id=collection_id,
            type=LogType.REMINDER_SCHEDULED,
            message=f"리마인더 예약: {reminder_date}",
        )
        db.add(reminder_log)
    
    db.commit()
    db.refresh(notice_log)
    
    return NoticeOut(
        success=True,
        message=message,
        log_id=notice_log.id,
    )

