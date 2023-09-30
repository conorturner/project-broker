"""Schemas for API error response types."""

from pydantic import BaseModel


class EntityNotFound(BaseModel):
    """Not found error."""
    message: str


class DuplicateEntity(BaseModel):
    """Duplicate entity error."""
    message: str
