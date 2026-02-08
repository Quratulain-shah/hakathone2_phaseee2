"""
Database utilities for the Todo App backend API
"""
from typing import AsyncGenerator
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy import event
from sqlalchemy.engine import Engine

try:
    from config import settings
except ImportError:
    from backend.config import settings

# Create async engine for the database
# For SQLite, use StaticPool and disable some pooling features
if settings.DATABASE_URL.startswith("sqlite"):
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=StaticPool,
        echo=True,  # Enable for debugging
        connect_args={"check_same_thread": False}
    )
else:
    from sqlalchemy.pool import NullPool
    # Use NullPool for Neon PostgreSQL to avoid prepared statement cache issues
    # with pgbouncer connection pooling
    # Disable prepared statement cache to work with Neon's connection pooler
    async_engine = create_async_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        echo=False,
        connect_args={
            "prepared_statement_cache_size": 0,
            "statement_cache_size": 0,
        },
    )


async def create_db_and_tables():
    """
    Create database tables
    This is primarily for testing purposes in Phase 2
    """
    try:
        try:
            from models.user import User  # Import to register the model
            from models.task import Task  # Import to register the model
        except ImportError:
            from backend.models.user import User
            from backend.models.task import Task

        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
    except Exception as e:
        # In production or shared databases, we might not have permission to create tables
        # Log the error but don't crash the application
        print(f"Warning: Could not create database tables: {str(e)}")
        print("This is expected in production environments where tables are pre-created")


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session
    """
    async with AsyncSession(async_engine) as session:
        yield session