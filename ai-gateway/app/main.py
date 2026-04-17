"""FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database import init_db
from app.api import chat_router, images_router, admin_router

# Create FastAPI app
app = FastAPI(
    title="AI Gateway",
    description="Unified AI Model API Gateway",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(chat_router)
app.include_router(images_router)
app.include_router(admin_router)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    init_db()


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "AI Gateway",
        "version": "1.0.0",
        "endpoints": {
            "chat": "/v1/chat/completions",
            "images": "/v1/images/generations",
            "admin": "/admin"
        }
    }
