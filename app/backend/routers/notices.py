"""Notices router."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.backend.db.session import get_db
from app.backend.schemas.total_manager import NoticeCreate, NoticeOut
from app.backend.services.notices_service import send_notice

router = APIRouter(prefix="/total-manager", tags=["notices"])


# Temporary auth dependency - replace with actual auth when available
def get_current_user_id() -> str:
    """Get current user ID. TODO: Replace with actual auth."""
    return "user_123"


@router.post("/collections/{collection_id}/notice", response_model=NoticeOut)
def send_notice_endpoint(
    collection_id: str,
    notice_data: NoticeCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Send a notice for a collection."""
    return send_notice(db, collection_id, user_id, notice_data)

