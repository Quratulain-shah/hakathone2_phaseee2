"""
Main FastAPI application for the Todo App backend API
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import sys

# Add the current directory to the path for both local and HF deployment
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
# Also add parent directory for local development with `backend.` imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Try relative imports first (for HF deployment)
    from config import settings
    from database import create_db_and_tables
    from routes import tasks
    from routes import auth
except ImportError:
    # Fall back to absolute imports (for local development)
    from backend.config import settings
    from backend.database import create_db_and_tables
    from backend.routes import tasks
    from backend.routes import auth


# Create FastAPI application instance
app = FastAPI(
    title=settings.PROJECT_NAME,
    version="1.0.0",
    description="Todo App Backend API - Phase 3 Implementation with Authentication",
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def on_startup():
    """
    Initialize database tables on startup
    """
    await create_db_and_tables()


# Include the auth and tasks routers
app.include_router(auth.router, prefix=settings.API_V1_STR, tags=["auth"])
app.include_router(tasks.router, prefix=settings.API_V1_STR, tags=["tasks"])


@app.get("/")
async def root():
    """
    Root endpoint for health check
    """
    return {"message": "Todo App Backend API - Phase 3 with Authentication", "status": "running"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)