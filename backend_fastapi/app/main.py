from __future__ import annotations

import os
from typing import List, Optional

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from app.models.api import CategoriesResponse, ErrorResponse, NewsItem, NewsListResponse
from app.services.aggregator import NewsAggregator


def _get_allowed_origins() -> list[str]:
    """
    Resolve allowed origins from env.

    Supports:
    - ALLOWED_ORIGINS="https://a.com,http://localhost:3000"
    - FRONTEND_URL="http://localhost:3000" as a fallback
    - ALLOWED_ORIGINS="*" to explicitly allow any origin (use with caution)
    """
    allowed = os.getenv("ALLOWED_ORIGINS", "").strip()
    if allowed:
        if allowed == "*":
            return ["*"]
        return [o.strip() for o in allowed.split(",") if o.strip()]

    frontend_url = os.getenv("FRONTEND_URL", "").strip()
    if frontend_url:
        return [frontend_url]

    # Safe dev default (matches plan requirement: allow frontend on :3000)
    return [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        # Vite default port (in case configuration changes)
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]


openapi_tags = [
    {
        "name": "Health",
        "description": "Service health and diagnostics endpoints.",
    },
    {
        "name": "News",
        "description": "Normalized Boca Juniors news aggregation endpoints.",
    },
]

app = FastAPI(
    title="Boca News Aggregator API",
    description=(
        "Aggregates Boca Juniors news from multiple sources (seed data first; extensible "
        "to RSS/JSON sources) and exposes a normalized REST API for the frontend."
    ),
    version="1.0.0",
    openapi_tags=openapi_tags,
)

# CORS: allow the frontend container to call the API from a browser.
app.add_middleware(
    CORSMiddleware,
    allow_origins=_get_allowed_origins(),
    allow_credentials=True,
    allow_methods=[m.strip() for m in os.getenv("ALLOWED_METHODS", "GET,OPTIONS").split(",") if m.strip()],
    allow_headers=[h.strip() for h in os.getenv("ALLOWED_HEADERS", "Content-Type,Authorization").split(",") if h.strip()],
    max_age=int(os.getenv("CORS_MAX_AGE", "3600")),
)

# Aggregator is currently in-memory + seed sources; designed to be extended with RSS/JSON.
aggregator = NewsAggregator()


@app.get(
    "/healthz",
    tags=["Health"],
    summary="Health check",
    description="Returns basic health information for readiness/liveness checks.",
    response_model=dict,
    operation_id="healthz",
)
def healthz() -> dict:
    """Health check endpoint.

    Returns:
        A small JSON payload containing service status.
    """
    return {"status": "ok"}


@app.get(
    "/categories",
    tags=["News"],
    summary="List categories",
    description="Returns available news categories derived from the aggregated sources.",
    response_model=CategoriesResponse,
    operation_id="list_categories",
    responses={500: {"model": ErrorResponse}},
)
# PUBLIC_INTERFACE
def list_categories() -> CategoriesResponse:
    """Return all categories.

    Returns:
        CategoriesResponse: List of normalized categories.
    """
    categories = aggregator.get_categories()
    return CategoriesResponse(categories=categories)


@app.get(
    "/news",
    tags=["News"],
    summary="List news items",
    description=(
        "Returns a normalized list of news items. Supports optional full-text search "
        "and category filtering."
    ),
    response_model=NewsListResponse,
    operation_id="list_news",
    responses={500: {"model": ErrorResponse}},
)
# PUBLIC_INTERFACE
def list_news(
    q: Optional[str] = Query(
        default=None,
        description="Optional search query (matches title, summary, and source name).",
        min_length=1,
        max_length=200,
    ),
    category: Optional[str] = Query(
        default=None,
        description="Optional category filter. Must match one of /categories values.",
        min_length=1,
        max_length=64,
    ),
    limit: int = Query(
        default=50,
        description="Maximum number of items to return.",
        ge=1,
        le=200,
    ),
    offset: int = Query(
        default=0,
        description="Offset into the result set (for simple pagination).",
        ge=0,
        le=10000,
    ),
) -> NewsListResponse:
    """List news items with optional filtering.

    Args:
        q: Optional search string.
        category: Optional category filter.
        limit: Max items returned.
        offset: Starting offset.

    Returns:
        NewsListResponse: normalized items and metadata.
    """
    items, total = aggregator.list_news(q=q, category=category, limit=limit, offset=offset)
    return NewsListResponse(items=items, total=total, limit=limit, offset=offset, q=q, category=category)


@app.get(
    "/news/{news_id}",
    tags=["News"],
    summary="Get a news item by id",
    description="Fetch a single normalized news item by its id.",
    response_model=NewsItem,
    operation_id="get_news_by_id",
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
# PUBLIC_INTERFACE
def get_news_by_id(news_id: str) -> NewsItem:
    """Get a single news item.

    Args:
        news_id: The normalized item id.

    Returns:
        NewsItem: the matching item.

    Raises:
        HTTPException: if not found.
    """
    return aggregator.get_news_by_id(news_id)
