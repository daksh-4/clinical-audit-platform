"""
Base class for SQLAlchemy models.
"""
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String
from datetime import datetime
from typing import Any
import uuid


class Base(DeclarativeBase):
    """
    Base class for all database models.
    """
    pass


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps.
    """
    created_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class UUIDMixin:
    """
    Mixin to add UUID primary key.
    """
    id: Mapped[uuid.UUID] = mapped_column(
        String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4()),
    )
