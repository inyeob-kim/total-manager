"""Logs service layer."""
from sqlalchemy.orm import Session
from typing import List, Optional
from collections import defaultdict

from app.backend.db.models.total_manager import TMEventLog, TMGroup, TMCollection, LogType
from app.backend.schemas.total_manager import EventLogOut, LogStatsOut
from app.backend.services.common import verify_collection_access


def list_logs(db: Session, collection_id: str, owner_id: str) -> List[TMEventLog]:
    """List all logs for a collection."""
    verify_collection_access(db, collection_id, owner_id)
    return (
        db.query(TMEventLog)
        .filter(TMEventLog.collection_id == collection_id)
        .order_by(TMEventLog.created_at.desc())
        .all()
    )


def list_all_logs(
    db: Session,
    user_id: str,
    collection_id: Optional[str] = None,
    log_type: Optional[LogType] = None,
    limit: int = 50,
    offset: int = 0
) -> dict:
    """List all logs for a user."""
    # Get user's groups
    groups = db.query(TMGroup).filter(TMGroup.owner_id == user_id).all()
    group_ids = [g.id for g in groups]
    
    # Get collections from user's groups
    collections = db.query(TMCollection).filter(
        TMCollection.group_id.in_(group_ids)
    ).all()
    collection_ids = [c.id for c in collections]
    
    query = db.query(TMEventLog).filter(
        TMEventLog.collection_id.in_(collection_ids)
    )
    
    if collection_id:
        query = query.filter(TMEventLog.collection_id == collection_id)
    if log_type:
        query = query.filter(TMEventLog.type == log_type)
    
    total = query.count()
    logs = query.order_by(TMEventLog.created_at.desc()).offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "logs": logs,
    }


def get_log_stats(db: Session, user_id: str) -> LogStatsOut:
    """Get log statistics for a user."""
    groups = db.query(TMGroup).filter(TMGroup.owner_id == user_id).all()
    group_ids = [g.id for g in groups]
    
    collections = db.query(TMCollection).filter(
        TMCollection.group_id.in_(group_ids)
    ).all()
    collection_ids = [c.id for c in collections]
    
    logs = db.query(TMEventLog).filter(
        TMEventLog.collection_id.in_(collection_ids)
    ).all()
    
    by_type = {}
    for log_type in LogType:
        by_type[log_type.value] = sum(1 for log in logs if log.type == log_type)
    
    # Recent activity (by date)
    recent_activity_dict = defaultdict(int)
    for log in logs:
        date_key = log.created_at.date().isoformat()
        recent_activity_dict[date_key] += 1
    
    return LogStatsOut(
        total_logs=len(logs),
        by_type=by_type,
        recent_activity=[
            {"date": date, "count": count}
            for date, count in sorted(recent_activity_dict.items(), reverse=True)[:7]
        ],
    )

