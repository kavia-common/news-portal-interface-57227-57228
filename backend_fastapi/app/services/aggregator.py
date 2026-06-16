from __future__ import annotations

import hashlib
import re
from datetime import datetime, timezone
from typing import Any, Iterable, Optional, Tuple

from fastapi import HTTPException

from app.models.api import NewsItem
from app.services.seed_data import seed_items


def _parse_dt(value: str) -> datetime:
    """Parse ISO timestamp strings to timezone-aware datetimes."""
    # datetime.fromisoformat supports offsets; we normalize to UTC.
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def _stable_id(*parts: str) -> str:
    """Generate a stable, short id from key parts."""
    h = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()
    return h[:16]


def _normalize_text(s: str) -> str:
    """Normalize text for matching."""
    return re.sub(r"\s+", " ", (s or "").strip()).lower()


class NewsAggregator:
    """Aggregates news from multiple sources and returns normalized items.

    Currently uses a seed dataset. Designed to be extended by adding additional
    source loaders (RSS/JSON) that yield raw dicts and feed into normalization.
    """

    def __init__(self) -> None:
        self._raw_items: list[dict[str, Any]] = []
        self._refresh()

    def _refresh(self) -> None:
        """Load items from configured sources (seed-first)."""
        self._raw_items = []
        self._raw_items.extend(seed_items())

    def _iter_normalized(self) -> Iterable[NewsItem]:
        """Yield normalized items from raw dicts."""
        for raw in self._raw_items:
            title = str(raw.get("title", "")).strip()
            url = str(raw.get("url", "")).strip()
            source = str(raw.get("source", "Unknown")).strip() or "Unknown"
            category = str(raw.get("category", "General")).strip() or "General"
            summary = str(raw.get("summary", "")).strip()
            image_url = raw.get("image_url")
            published_at_raw = str(raw.get("published_at", "")).strip()

            if not title or not url:
                # Skip malformed items (future sources may be noisy).
                continue

            news_id = _stable_id(url, title, source)
            published_at = _parse_dt(published_at_raw) if published_at_raw else datetime.now(tz=timezone.utc)

            yield NewsItem(
                id=news_id,
                title=title,
                summary=summary,
                url=url,
                image_url=str(image_url).strip() if image_url else None,
                published_at=published_at,
                source=source,
                category=category,
            )

    def get_categories(self) -> list[str]:
        """Return unique sorted categories."""
        categories = {item.category for item in self._iter_normalized()}
        return sorted(categories, key=lambda x: x.lower())

    def list_news(
        self,
        q: Optional[str],
        category: Optional[str],
        limit: int,
        offset: int,
    ) -> Tuple[list[NewsItem], int]:
        """List news items with optional filters.

        Filtering behavior:
        - category: case-insensitive exact match
        - q: simple substring match across title, summary, source, category
        """
        normalized_items = list(self._iter_normalized())

        if category:
            cat_norm = _normalize_text(category)
            normalized_items = [i for i in normalized_items if _normalize_text(i.category) == cat_norm]

        if q:
            qn = _normalize_text(q)
            normalized_items = [
                i
                for i in normalized_items
                if qn in _normalize_text(i.title)
                or qn in _normalize_text(i.summary)
                or qn in _normalize_text(i.source)
                or qn in _normalize_text(i.category)
            ]

        # Newest first
        normalized_items.sort(key=lambda i: i.published_at, reverse=True)

        total = len(normalized_items)
        sliced = normalized_items[offset : offset + limit]
        return sliced, total

    def get_news_by_id(self, news_id: str) -> NewsItem:
        """Fetch a single item by id."""
        for item in self._iter_normalized():
            if item.id == news_id:
                return item
        raise HTTPException(status_code=404, detail=f"News item '{news_id}' not found")
