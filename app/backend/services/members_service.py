"""Members service layer."""
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List

from app.backend.db.models.total_manager import TMMemberStatus, TMEventLog, LogType
from app.backend.schemas.total_manager import (
    MemberCreate,
    MemberOut,
    MemberUpdate,
    BulkMemberCreate,
)
from app.backend.services.common import verify_collection_access, verify_member_access
from app.backend.utils.ulid import generate_ulid


def add_member(
    db: Session,
    collection_id: str,
    owner_id: str,
    member_data: MemberCreate
) -> TMMemberStatus:
    """Add a member to a collection."""
    verify_collection_access(db, collection_id, owner_id)
    
    member = TMMemberStatus(
        id=generate_ulid(),
        collection_id=collection_id,
        display_name=member_data.display_name,
        phone=member_data.phone,
    )
    db.add(member)
    db.commit()
    db.refresh(member)
    return member


def list_members(db: Session, collection_id: str, owner_id: str) -> List[TMMemberStatus]:
    """List all members for a collection."""
    verify_collection_access(db, collection_id, owner_id)
    return db.query(TMMemberStatus).filter(TMMemberStatus.collection_id == collection_id).all()


def update_member(
    db: Session,
    member_id: str,
    owner_id: str,
    member_data: MemberUpdate
) -> TMMemberStatus:
    """Update a member."""
    member = verify_member_access(db, member_id, owner_id)
    
    if member_data.display_name is not None:
        member.display_name = member_data.display_name
    if member_data.phone is not None:
        member.phone = member_data.phone
    
    db.commit()
    db.refresh(member)
    return member


def delete_member(db: Session, member_id: str, owner_id: str) -> None:
    """Delete a member."""
    member = verify_member_access(db, member_id, owner_id)
    db.delete(member)
    db.commit()


def bulk_add_members(
    db: Session,
    collection_id: str,
    owner_id: str,
    bulk_data: BulkMemberCreate
) -> dict:
    """Add multiple members at once."""
    verify_collection_access(db, collection_id, owner_id)
    
    created = []
    failed = []
    
    for member_data in bulk_data.members:
        try:
            member = TMMemberStatus(
                id=generate_ulid(),
                collection_id=collection_id,
                display_name=member_data.display_name,
                phone=member_data.phone,
            )
            db.add(member)
            created.append(member)
        except Exception as e:
            failed.append({"member": member_data.model_dump(), "error": str(e)})
    
    db.commit()
    
    # Refresh created members
    for member in created:
        db.refresh(member)
    
    return {
        "created": len(created),
        "failed": len(failed),
        "members": created,
        "errors": failed if failed else None,
    }


def mark_read(db: Session, member_id: str, owner_id: str) -> TMMemberStatus:
    """Mark a member as read."""
    member = verify_member_access(db, member_id, owner_id)
    
    member.read_at = datetime.now(timezone.utc)
    
    # Create read log
    read_log = TMEventLog(
        id=generate_ulid(),
        collection_id=member.collection_id,
        type=LogType.READ,
        message=f"{member.display_name}님이 읽음 처리했습니다.",
    )
    db.add(read_log)
    
    db.commit()
    db.refresh(member)
    
    return member


def mark_paid(db: Session, member_id: str, owner_id: str) -> TMMemberStatus:
    """Mark a member as paid."""
    member = verify_member_access(db, member_id, owner_id)
    
    member.paid_at = datetime.now(timezone.utc)
    
    # Create paid_marked log
    paid_log = TMEventLog(
        id=generate_ulid(),
        collection_id=member.collection_id,
        type=LogType.PAID_MARKED,
        message=f"{member.display_name}님이 납부 처리했습니다.",
    )
    db.add(paid_log)
    
    db.commit()
    db.refresh(member)
    
    return member

