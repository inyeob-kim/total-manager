"""User settings router."""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session
from typing import List

from app.backend.db.session import get_db
from app.backend.schemas.user_settings import (
    NotificationSettingsOut,
    NotificationSettingsUpdate,
    PaymentMethodOut,
    PaymentMethodCreate,
    PaymentMethodUpdate,
)
from app.backend.services.user_settings_service import (
    get_notification_settings,
    update_notification_settings,
    list_payment_methods,
    get_payment_method,
    create_payment_method,
    update_payment_method,
    delete_payment_method,
    set_default_payment_method,
)

router = APIRouter(prefix="/users/me", tags=["user-settings"])


# Temporary auth dependency - replace with actual auth when available
def get_current_user_id() -> str:
    """Get current user ID. TODO: Replace with actual auth."""
    return "user_123"


# Notification settings endpoints
@router.get("/settings/notifications", response_model=NotificationSettingsOut)
def get_notification_settings_endpoint(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get notification settings for the current user."""
    return get_notification_settings(db, user_id)


@router.patch("/settings/notifications", response_model=NotificationSettingsOut)
def update_notification_settings_endpoint(
    settings_data: NotificationSettingsUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update notification settings."""
    return update_notification_settings(db, user_id, settings_data)


# Payment methods endpoints
@router.get("/payment-methods", response_model=List[PaymentMethodOut])
def list_payment_methods_endpoint(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """List payment methods for the current user."""
    return list_payment_methods(db, user_id)


@router.post("/payment-methods", response_model=PaymentMethodOut, status_code=status.HTTP_201_CREATED)
def create_payment_method_endpoint(
    payment_data: PaymentMethodCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Create a new payment method."""
    return create_payment_method(db, user_id, payment_data)


@router.get("/payment-methods/{payment_method_id}", response_model=PaymentMethodOut)
def get_payment_method_endpoint(
    payment_method_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Get a payment method by ID."""
    from app.backend.services.user_settings_service import verify_payment_method_access
    return verify_payment_method_access(db, payment_method_id, user_id)


@router.patch("/payment-methods/{payment_method_id}", response_model=PaymentMethodOut)
def update_payment_method_endpoint(
    payment_method_id: str,
    payment_data: PaymentMethodUpdate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Update a payment method."""
    return update_payment_method(db, payment_method_id, user_id, payment_data)


@router.delete("/payment-methods/{payment_method_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_payment_method_endpoint(
    payment_method_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Delete a payment method."""
    delete_payment_method(db, payment_method_id, user_id)
    return None


@router.post("/payment-methods/{payment_method_id}/set-default", response_model=PaymentMethodOut)
def set_default_payment_method_endpoint(
    payment_method_id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Set a payment method as default."""
    return set_default_payment_method(db, payment_method_id, user_id)

