"""Pydantic models for OT-Croissant curation assets."""
from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class RecordsetFieldAnnotation(BaseModel):
    """Annotation for a single field within a recordset dataset."""

    model_config = ConfigDict(populate_by_name=True)

    id: str
    description: str
    is_primary_key: bool = Field(default=False, alias="isPrimaryKey")
    foreign_key: str | None = None


class DistributionAnnotation(BaseModel):
    """Annotation for a top-level dataset distribution."""

    id: str
    nice_name: str
    description: str
    tags: list[str] = []
    key: list[str] | str | None = None


class InstanceAnnotation(BaseModel):
    """Annotation for a Platform instance (public / ppp)."""

    id: str
    name: str
    description: str
    license: str
    url: str
