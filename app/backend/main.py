"""FastAPI application main file."""
from fastapi import FastAPI
from app.backend.routers import (
    auth,
    groups,
    collections,
    members,
    logs,
    notices,
    reminders,
    user_settings,
)

app = FastAPI(title="Total Manager API", version="1.0.0")

# Include routers
app.include_router(auth.router)
app.include_router(groups.router)
app.include_router(collections.router)
app.include_router(members.router)
app.include_router(logs.router)
app.include_router(notices.router)
app.include_router(reminders.router)
app.include_router(user_settings.router)

@app.get("/")
def root():
    """Root endpoint."""
    return {"message": "Total Manager API"}

@app.get("/health")
def health():
    """Health check endpoint."""
    return {"status": "ok"}

