"""Custom Prometheus metrics.

Kept in a dedicated module so any router can import without pulling in the
FastAPI app object. HTTP request metrics (count, latency histogram, size) are
added by `prometheus_fastapi_instrumentator` in `app.main` — this file only
declares the app-specific series.
"""

import platform

from prometheus_client import Counter, Gauge, Info

ITEMS_TOTAL = Gauge(
    "app_items_total",
    "Current number of items in the in-memory store.",
)

ITEMS_CREATED_TOTAL = Counter(
    "app_items_created_total",
    "Total number of items ever created since process start.",
)

APP_INFO = Info(
    "app_build",
    "Application build information.",
)


def init_app_info(name: str, version: str) -> None:
    """Populate `app_build_info` with static labels. Call once at startup."""
    APP_INFO.info(
        {
            "name": name,
            "version": version,
            "python_version": platform.python_version(),
        }
    )
