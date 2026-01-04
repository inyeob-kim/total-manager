"""Common utility functions for Total Manager services."""
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status

from app.backend.db.models.total_manager import TMGroup, TMCollection, TMMemberStatus


def get_group(db: Session, group_id: str) -> Optional[TMGroup]:
    """Get a group by ID."""
    return db.query(TMGroup).filter(TMGroup.id == group_id).first()


def verify_group_owner(db: Session, group_id: str, owner_id: str) -> TMGroup:
    """Verify group exists and belongs to owner."""
    group = get_group(db, group_id)
    if not group:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Group not found"
        )
    if group.owner_id != owner_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return group


def get_collection(db: Session, collection_id: str) -> Optional[TMCollection]:
    """Get a collection by ID."""
    return db.query(TMCollection).filter(TMCollection.id == collection_id).first()


def verify_collection_access(db: Session, collection_id: str, owner_id: str) -> TMCollection:
    """Verify collection exists and user has access."""
    collection = get_collection(db, collection_id)
    if not collection:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Collection not found"
        )
    # Verify through group ownership
    verify_group_owner(db, collection.group_id, owner_id)
    return collection


def get_member(db: Session, member_id: str) -> Optional[TMMemberStatus]:
    """Get a member by ID."""
    return db.query(TMMemberStatus).filter(TMMemberStatus.id == member_id).first()


def verify_member_access(db: Session, member_id: str, owner_id: str) -> TMMemberStatus:
    """Verify member exists and user has access."""
    member = get_member(db, member_id)
    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )
    # Verify through collection and group ownership
    verify_collection_access(db, member.collection_id, owner_id)
    return member

