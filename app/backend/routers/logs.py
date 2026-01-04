"""Logs router."""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.backend.db.session import get_db
from app.backend.db.models.total_manager import LogType
from app.backend.schemas.total_manager import EventLogOut, LogStatsOut
from app.backend.services.logs_service import (
    list_logs,
    list_all_logs,
    get_log_stats,
)

router = APIRouter(prefix="/total-manager", tags=["logs"])


# Temporary auth dependency - replace with actual auth when available
def get_current_user_id() -> str:
    """Get current user ID. TODO: Replace with actual auth."""
    return "user_123"


@router.get("/collections/{collection_id}/logs", response_model=List[EventLogOut])
def list_logs_endpoint(
    collection_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List all logs for a collection."""
    return list_logs(db, collection_id, user_id)


@router.get("/logs", response_model=dict)
def list_all_logs_endpoint(
    collection_id: Optional[str] = Query(None),
    log_type: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List all logs for the current user."""
    log_type_enum = None
    if log_type:
        try:
            log_type_enum = LogType(log_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid log_type: {log_type}"
            )
    return list_all_logs(db, user_id, collection_id=collection_id, log_type=log_type_enum, limit=limit, offset=offset)


@router.get("/logs/stats", response_model=LogStatsOut)
def get_log_stats_endpoint(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get log statistics for the current user."""
    return get_log_stats(db, user_id)

