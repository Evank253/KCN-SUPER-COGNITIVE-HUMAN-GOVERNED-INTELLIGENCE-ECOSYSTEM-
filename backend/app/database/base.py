"""
Declarative base for all SQLAlchemy models.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base class for all ORM models."""
