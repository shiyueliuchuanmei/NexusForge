"""API routes package."""
from app.api.chat import router as chat_router
from app.api.images import router as images_router
from app.api.admin import router as admin_router

__all__ = ["chat_router", "images_router", "admin_router"]
