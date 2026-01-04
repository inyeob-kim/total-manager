"""Groups service layer."""
from sqlalchemy.orm import Session
from typing import List

from app.backend.db.models.total_manager import TMGroup, GroupType
from app.backend.schemas.total_manager import GroupCreate, GroupOut, GroupUpdate, GroupDetailOut
from app.backend.services.common import verify_group_owner, get_group
from app.backend.utils.ulid import generate_ulid


def create_group(db: Session, owner_id: str, group_data: GroupCreate) -> TMGroup:
    """Create a new group."""
    # Normalize and validate type
    type_str = group_data.type.lower() if isinstance(group_data.type, str) else str(group_data.type).lower()
    
    # Map string to enum
    type_mapping = {
        'parents': GroupType.PARENTS,
        'club': GroupType.CLUB,
        'study': GroupType.STUDY,
        'other': GroupType.OTHER,
    }
    
    # Map to enum value string directly
    group_type_value = type_mapping.get(type_str, GroupType.OTHER).value
    
    group = TMGroup(
        id=generate_ulid(),
        owner_id=owner_id,
        name=group_data.name,
        type=group_type_value,  # Store as string value (e.g., "other")
    )
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def list_groups(db: Session, owner_id: str) -> List[TMGroup]:
    """List all groups for an owner."""
    return db.query(TMGroup).filter(TMGroup.owner_id == owner_id).all()


def get_group_detail(db: Session, group_id: str, owner_id: str) -> GroupDetailOut:
    """Get group detail with statistics."""
    group = verify_group_owner(db, group_id, owner_id)
    
    from app.backend.db.models.total_manager import TMCollection
    collections = db.query(TMCollection).filter(TMCollection.group_id == group_id).all()
    collections_count = len(collections)
    total_amount = sum(c.amount for c in collections)
    
    return GroupDetailOut(
        id=group.id,
        owner_id=group.owner_id,
        name=group.name,
        type=group.type,
        created_at=group.created_at,
        collections_count=collections_count,
        total_amount=total_amount,
    )


def update_group(
    db: Session,
    group_id: str,
    owner_id: str,
    group_data: GroupUpdate
) -> TMGroup:
    """Update a group."""
    group = verify_group_owner(db, group_id, owner_id)
    
    if group_data.name is not None:
        group.name = group_data.name
    if group_data.type is not None:
        # Normalize and validate type
        type_str = group_data.type.lower() if isinstance(group_data.type, str) else str(group_data.type).lower()
        type_mapping = {
            'parents': GroupType.PARENTS,
            'club': GroupType.CLUB,
            'study': GroupType.STUDY,
            'other': GroupType.OTHER,
        }
        group_type_value = type_mapping.get(type_str, GroupType.OTHER).value
        group.type = group_type_value  # Store as string value
    
    db.commit()
    db.refresh(group)
    return group


def delete_group(db: Session, group_id: str, owner_id: str) -> None:
    """Delete a group."""
    group = verify_group_owner(db, group_id, owner_id)
    db.delete(group)
    db.commit()

