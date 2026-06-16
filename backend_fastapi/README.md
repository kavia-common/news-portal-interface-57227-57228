# backend_fastapi — Boca News Aggregator API

FastAPI backend that aggregates Boca Juniors news (seed data first; extensible to RSS/JSON sources) and exposes REST endpoints for the frontend.

## Endpoints

- `GET /healthz`
- `GET /categories`
- `GET /news?q=...&category=...&limit=...&offset=...`
- `GET /news/{id}`

## Configuration

Environment variables (already present in `.env` in this template):

- `PORT` (default expected: `3001`)
- `ALLOWED_ORIGINS` (comma-separated) or `FRONTEND_URL`

## Run (example)

```bash
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 3001
```
