"""Collections service layer."""
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.backend.db.models.total_manager import TMCollection, CollectionStatus, PaymentType
from app.backend.schemas.total_manager import (
    CollectionCreate,
    CollectionOut,
    CollectionUpdate,
    CollectionSummaryOut,
)
from app.backend.services.common import verify_group_owner, verify_collection_access
from app.backend.utils.ulid import generate_ulid


def create_collection(
    db: Session,
    group_id: str,
    owner_id: str,
    collection_data: CollectionCreate
) -> TMCollection:
    """Create a new collection."""
    # Verify group ownership
    verify_group_owner(db, group_id, owner_id)
    
    # Determine status based on due_date
    today = date.today()
    status_value = 'active'
    if collection_data.due_date <= today:
        status_value = 'closed'
    elif (collection_data.due_date - today).days <= 3:
        status_value = 'due_soon'
    
    # Normalize and validate payment_type
    payment_type_value = collection_data.payment_type
    if isinstance(payment_type_value, PaymentType):
        payment_type_value = payment_type_value.value
    elif isinstance(payment_type_value, str):
        payment_type_value = payment_type_value.lower()
    else:
        payment_type_value = str(payment_type_value).lower()
    
    # Map string to enum for validation
    if payment_type_value not in ['bank', 'link']:
        payment_type_value = 'bank'  # Default to bank
    
    collection = TMCollection(
        id=generate_ulid(),
        group_id=group_id,
        title=collection_data.title,
        amount=collection_data.amount,
        due_date=collection_data.due_date,
        payment_type=payment_type_value,
        payment_value=collection_data.payment_value,
        status=status_value,
    )
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


def list_collections(db: Session, group_id: str, owner_id: str) -> List[TMCollection]:
    """List all collections for a group."""
    verify_group_owner(db, group_id, owner_id)
    return db.query(TMCollection).filter(TMCollection.group_id == group_id).all()


def update_collection(
    db: Session,
    collection_id: str,
    owner_id: str,
    collection_data: CollectionUpdate
) -> TMCollection:
    """Update a collection."""
    collection = verify_collection_access(db, collection_id, owner_id)
    
    if collection_data.title is not None:
        collection.title = collection_data.title
    if collection_data.amount is not None:
        collection.amount = collection_data.amount
    if collection_data.due_date is not None:
        collection.due_date = collection_data.due_date
        # Recalculate status based on due_date
        today = date.today()
        if collection_data.due_date <= today:
            collection.status = 'closed'
        elif (collection_data.due_date - today).days <= 3:
            collection.status = 'due_soon'
        else:
            collection.status = 'active'
    if collection_data.payment_type is not None:
        # Normalize and validate payment_type
        payment_type_value = collection_data.payment_type
        if isinstance(payment_type_value, PaymentType):
            payment_type_value = payment_type_value.value
        elif isinstance(payment_type_value, str):
            payment_type_value = payment_type_value.lower()
        else:
            payment_type_value = str(payment_type_value).lower()
        
        # Map string to enum for validation
        if payment_type_value not in ['bank', 'link']:
            payment_type_value = 'bank'  # Default to bank
        
        collection.payment_type = payment_type_value
    if collection_data.payment_value is not None:
        collection.payment_value = collection_data.payment_value
    
    db.commit()
    db.refresh(collection)
    return collection


def delete_collection(db: Session, collection_id: str, owner_id: str) -> None:
    """Delete a collection."""
    collection = verify_collection_access(db, collection_id, owner_id)
    db.delete(collection)
    db.commit()


def get_collection_summary(
    db: Session,
    collection_id: str,
    owner_id: str
) -> CollectionSummaryOut:
    """Get collection summary with statistics."""
    collection = verify_collection_access(db, collection_id, owner_id)
    
    from app.backend.db.models.total_manager import TMMemberStatus
    members = db.query(TMMemberStatus).filter(
        TMMemberStatus.collection_id == collection_id
    ).all()
    
    total_members = len(members)
    read_members = sum(1 for m in members if m.read_at is not None)
    paid_members = sum(1 for m in members if m.paid_at is not None)
    
    # Calculate current amount (simple: paid_members * (amount / total_members))
    current_amount = int((paid_members / total_members * collection.amount)) if total_members > 0 else 0
    
    return CollectionSummaryOut(
        id=collection.id,
        title=collection.title,
        amount=collection.amount,
        due_date=collection.due_date,
        status=collection.status,
        total_members=total_members,
        read_members=read_members,
        paid_members=paid_members,
        current_amount=current_amount,
        payment_type=collection.payment_type,
        payment_value=collection.payment_value,
    )

