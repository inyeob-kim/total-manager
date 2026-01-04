"""Members router."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.backend.db.session import get_db
from app.backend.schemas.total_manager import (
    MemberCreate,
    MemberOut,
    MemberUpdate,
    BulkMemberCreate,
)
from app.backend.services.members_service import (
    add_member,
    list_members,
    update_member,
    delete_member,
    bulk_add_members,
    mark_read,
    mark_paid,
)

router = APIRouter(prefix="/total-manager", tags=["members"])


# Temporary auth dependency - replace with actual auth when available
def get_current_user_id() -> str:
    """Get current user ID. TODO: Replace with actual auth."""
    return "user_123"


@router.post(
    "/collections/{collection_id}/members",
    response_model=MemberOut,
    status_code=status.HTTP_201_CREATED
)
def add_member_endpoint(
    collection_id: str,
    member_data: MemberCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Add a member to a collection."""
    return add_member(db, collection_id, user_id, member_data)


@router.get("/collections/{collection_id}/members", response_model=List[MemberOut])
def list_members_endpoint(
    collection_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List all members for a collection."""
    return list_members(db, collection_id, user_id)


@router.patch("/members/{member_id}", response_model=MemberOut)
def update_member_endpoint(
    member_id: str,
    member_data: MemberUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update a member."""
    return update_member(db, member_id, user_id, member_data)


@router.delete("/members/{member_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_member_endpoint(
    member_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Delete a member."""
    delete_member(db, member_id, user_id)
    return None


@router.post("/collections/{collection_id}/members/bulk", response_model=dict)
def bulk_add_members_endpoint(
    collection_id: str,
    bulk_data: BulkMemberCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Add multiple members at once."""
    return bulk_add_members(db, collection_id, user_id, bulk_data)


@router.post("/members/{member_id}/read", response_model=MemberOut)
def mark_read_endpoint(
    member_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Mark a member as read."""
    return mark_read(db, member_id, user_id)


@router.post("/members/{member_id}/paid", response_model=MemberOut)
def mark_paid_endpoint(
    member_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Mark a member as paid."""
    return mark_paid(db, member_id, user_id)

