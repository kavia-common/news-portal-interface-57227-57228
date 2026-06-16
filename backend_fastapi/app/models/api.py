from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Standard error response model."""

    detail: str = Field(..., description="Human-readable error message.")


class NewsItem(BaseModel):
    """Normalized news item returned to the frontend."""

    id: str = Field(..., description="Stable normalized id for this item.")
    title: str = Field(..., description="News title/headline.")
    summary: str = Field(..., description="Short summary/excerpt (plain text).")
    url: str = Field(..., description="Canonical link to the article.")
    image_url: Optional[str] = Field(default=None, description="Optional image URL for card display.")
    published_at: datetime = Field(..., description="Publication timestamp (UTC when available).")
    source: str = Field(..., description="Source/provider name.")
    category: str = Field(..., description="Normalized category name (e.g., 'Club', 'Matches').")


class NewsListResponse(BaseModel):
    """Response envelope for /news list endpoint."""

    items: List[NewsItem] = Field(..., description="List of normalized news items.")
    total: int = Field(..., description="Total count after applying filters (before limit/offset).")
    limit: int = Field(..., description="Limit used for this request.")
    offset: int = Field(..., description="Offset used for this request.")
    q: Optional[str] = Field(default=None, description="Echo of search query.")
    category: Optional[str] = Field(default=None, description="Echo of category filter.")


class CategoriesResponse(BaseModel):
    """Response envelope for /categories endpoint."""

    categories: List[str] = Field(..., description="Available category names.")
