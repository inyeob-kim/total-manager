"""User settings service layer."""
from sqlalchemy.orm import Session
from typing import Optional
from fastapi import HTTPException, status

from app.backend.db.models.user_settings import UserSettings, UserPaymentMethod
from app.backend.schemas.user_settings import (
    NotificationSettingsUpdate,
    PaymentMethodCreate,
    PaymentMethodUpdate,
)
from app.backend.utils.ulid import generate_ulid


def get_or_create_user_settings(db: Session, user_id: str) -> UserSettings:
    """Get user settings or create default if not exists."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == user_id).first()
    if not settings:
        settings = UserSettings(
            id=generate_ulid(),
            user_id=user_id,
        )
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def get_notification_settings(db: Session, user_id: str) -> UserSettings:
    """Get notification settings for a user."""
    return get_or_create_user_settings(db, user_id)


def update_notification_settings(
    db: Session,
    user_id: str,
    settings_data: NotificationSettingsUpdate
) -> UserSettings:
    """Update notification settings."""
    settings = get_or_create_user_settings(db, user_id)
    
    if settings_data.push_notifications_enabled is not None:
        settings.push_notifications_enabled = settings_data.push_notifications_enabled
    if settings_data.email_notifications_enabled is not None:
        settings.email_notifications_enabled = settings_data.email_notifications_enabled
    if settings_data.reminder_notifications_enabled is not None:
        settings.reminder_notifications_enabled = settings_data.reminder_notifications_enabled
    
    db.commit()
    db.refresh(settings)
    return settings


def list_payment_methods(db: Session, user_id: str) -> list[UserPaymentMethod]:
    """List payment methods for a user."""
    return db.query(UserPaymentMethod).filter(
        UserPaymentMethod.user_id == user_id
    ).order_by(UserPaymentMethod.is_default.desc(), UserPaymentMethod.created_at.desc()).all()


def get_payment_method(db: Session, payment_method_id: str) -> Optional[UserPaymentMethod]:
    """Get a payment method by ID."""
    return db.query(UserPaymentMethod).filter(
        UserPaymentMethod.id == payment_method_id
    ).first()


def verify_payment_method_access(
    db: Session,
    payment_method_id: str,
    user_id: str
) -> UserPaymentMethod:
    """Verify payment method exists and belongs to user."""
    payment_method = get_payment_method(db, payment_method_id)
    if not payment_method:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment method not found"
        )
    if payment_method.user_id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    return payment_method


def create_payment_method(
    db: Session,
    user_id: str,
    payment_data: PaymentMethodCreate
) -> UserPaymentMethod:
    """Create a new payment method."""
    # If setting as default, unset other defaults
    if payment_data.is_default:
        db.query(UserPaymentMethod).filter(
            UserPaymentMethod.user_id == user_id,
            UserPaymentMethod.is_default == True
        ).update({"is_default": False})
    
    payment_method = UserPaymentMethod(
        id=generate_ulid(),
        user_id=user_id,
        bank_name=payment_data.bank_name,
        account_number=payment_data.account_number,
        account_holder=payment_data.account_holder,
        is_default=payment_data.is_default or False,
    )
    db.add(payment_method)
    db.commit()
    db.refresh(payment_method)
    return payment_method


def update_payment_method(
    db: Session,
    payment_method_id: str,
    user_id: str,
    payment_data: PaymentMethodUpdate
) -> UserPaymentMethod:
    """Update a payment method."""
    payment_method = verify_payment_method_access(db, payment_method_id, user_id)
    
    if payment_data.bank_name is not None:
        payment_method.bank_name = payment_data.bank_name
    if payment_data.account_number is not None:
        payment_method.account_number = payment_data.account_number
    if payment_data.account_holder is not None:
        payment_method.account_holder = payment_data.account_holder
    if payment_data.is_default is not None:
        # If setting as default, unset other defaults
        if payment_data.is_default:
            db.query(UserPaymentMethod).filter(
                UserPaymentMethod.user_id == user_id,
                UserPaymentMethod.is_default == True,
                UserPaymentMethod.id != payment_method_id
            ).update({"is_default": False})
        payment_method.is_default = payment_data.is_default
    
    db.commit()
    db.refresh(payment_method)
    return payment_method


def delete_payment_method(db: Session, payment_method_id: str, user_id: str) -> None:
    """Delete a payment method."""
    payment_method = verify_payment_method_access(db, payment_method_id, user_id)
    db.delete(payment_method)
    db.commit()


def set_default_payment_method(
    db: Session,
    payment_method_id: str,
    user_id: str
) -> UserPaymentMethod:
    """Set a payment method as default."""
    payment_method = verify_payment_method_access(db, payment_method_id, user_id)
    
    # Unset other defaults
    db.query(UserPaymentMethod).filter(
        UserPaymentMethod.user_id == user_id,
        UserPaymentMethod.is_default == True,
        UserPaymentMethod.id != payment_method_id
    ).update({"is_default": False})
    
    payment_method.is_default = True
    db.commit()
    db.refresh(payment_method)
    return payment_method

