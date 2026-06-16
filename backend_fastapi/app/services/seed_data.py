from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List


def seed_items() -> list[dict[str, Any]]:
    """Return a seed dataset for initial development.

    This unblocks the UI while keeping the aggregator extensible to future RSS/JSON sources.
    """
    now = datetime.now(tz=timezone.utc)
    return [
        {
            "title": "Boca Juniors: resumen del entrenamiento de hoy",
            "summary": "El plantel se entrenó en Ezeiza con foco en táctica y pelota parada.",
            "url": "https://example.com/boca-entrenamiento",
            "image_url": "https://picsum.photos/seed/boca1/800/450",
            "published_at": (now - timedelta(hours=6)).isoformat(),
            "source": "Seed",
            "category": "Club",
        },
        {
            "title": "Previo del próximo partido: análisis y posibles cambios",
            "summary": "El DT evalúa variantes en el mediocampo para el próximo encuentro.",
            "url": "https://example.com/boca-previa-partido",
            "image_url": "https://picsum.photos/seed/boca2/800/450",
            "published_at": (now - timedelta(days=1, hours=2)).isoformat(),
            "source": "Seed",
            "category": "Matches",
        },
        {
            "title": "Mercado de pases: rumores y novedades de Boca",
            "summary": "Se intensifican las conversaciones por refuerzos; mirá los nombres que suenan.",
            "url": "https://example.com/boca-mercado-pases",
            "image_url": "https://picsum.photos/seed/boca3/800/450",
            "published_at": (now - timedelta(days=2, hours=3)).isoformat(),
            "source": "Seed",
            "category": "Transfers",
        },
        {
            "title": "Juveniles: la reserva ganó y se ilusiona",
            "summary": "La reserva consiguió un triunfo clave y se mete en la pelea del torneo.",
            "url": "https://example.com/boca-reserva-gano",
            "image_url": "https://picsum.photos/seed/boca4/800/450",
            "published_at": (now - timedelta(days=3)).isoformat(),
            "source": "Seed",
            "category": "Youth",
        },
    ]
