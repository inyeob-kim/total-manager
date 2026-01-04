"""Groups router."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.backend.db.session import get_db
from app.backend.schemas.total_manager import GroupCreate, GroupOut, GroupUpdate, GroupDetailOut
from app.backend.services.groups_service import (
    create_group,
    list_groups,
    get_group_detail,
    update_group,
    delete_group,
)

router = APIRouter(prefix="/total-manager/groups", tags=["groups"])


# Temporary auth dependency - replace with actual auth when available
def get_current_user_id() -> str:
    """Get current user ID. TODO: Replace with actual auth."""
    return "user_123"


@router.post("", response_model=GroupOut, status_code=status.HTTP_201_CREATED)
def create_group_endpoint(
    group_data: GroupCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Create a new group."""
    return create_group(db, user_id, group_data)


@router.get("", response_model=List[GroupOut])
def list_groups_endpoint(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List all groups for the current user."""
    return list_groups(db, user_id)


@router.get("/{group_id}", response_model=GroupDetailOut)
def get_group_endpoint(
    group_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get a group by ID with statistics."""
    return get_group_detail(db, group_id, user_id)


@router.patch("/{group_id}", response_model=GroupOut)
def update_group_endpoint(
    group_id: str,
    group_data: GroupUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update a group."""
    return update_group(db, group_id, user_id, group_data)


@router.delete("/{group_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_group_endpoint(
    group_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Delete a group."""
    delete_group(db, group_id, user_id)
    return None

