"""Routers package."""
from app.backend.routers import (
    groups,
    collections,
    members,
    logs,
    notices,
    reminders,
    user_settings,
)

__all__ = [
    "groups",
    "collections",
    "members",
    "logs",
    "notices",
    "reminders",
    "user_settings",
]
