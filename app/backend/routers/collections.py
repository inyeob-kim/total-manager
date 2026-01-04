"""Collections router."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.backend.db.session import get_db
from app.backend.schemas.total_manager import (
    CollectionCreate,
    CollectionOut,
    CollectionUpdate,
    CollectionSummaryOut,
)
from app.backend.services.collections_service import (
    create_collection,
    list_collections,
    update_collection,
    delete_collection,
    get_collection_summary,
)
from app.backend.services.common import verify_collection_access

router = APIRouter(prefix="/total-manager", tags=["collections"])


# Temporary auth dependency - replace with actual auth when available
def get_current_user_id() -> str:
    """Get current user ID. TODO: Replace with actual auth."""
    return "user_123"


@router.post(
    "/groups/{group_id}/collections",
    response_model=CollectionOut,
    status_code=status.HTTP_201_CREATED
)
def create_collection_endpoint(
    group_id: str,
    collection_data: CollectionCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Create a new collection."""
    return create_collection(db, group_id, user_id, collection_data)


@router.get("/groups/{group_id}/collections", response_model=List[CollectionOut])
def list_collections_endpoint(
    group_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List all collections for a group."""
    return list_collections(db, group_id, user_id)


@router.get("/collections/{collection_id}", response_model=CollectionOut)
def get_collection_endpoint(
    collection_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get a collection by ID."""
    return verify_collection_access(db, collection_id, user_id)


@router.patch("/collections/{collection_id}", response_model=CollectionOut)
def update_collection_endpoint(
    collection_id: str,
    collection_data: CollectionUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update a collection."""
    return update_collection(db, collection_id, user_id, collection_data)


@router.delete("/collections/{collection_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_collection_endpoint(
    collection_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Delete a collection."""
    delete_collection(db, collection_id, user_id)
    return None


@router.get("/collections/{collection_id}/summary", response_model=CollectionSummaryOut)
def get_collection_summary_endpoint(
    collection_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get collection summary with statistics."""
    return get_collection_summary(db, collection_id, user_id)

