"""Observability endpoints: /health, /readiness, /info."""

import os
import platform
import socket
import time

from fastapi import APIRouter

router = APIRouter(tags=["observability"])

_STARTUP_TIME = time.time()
_APP_NAME = os.getenv("APP_NAME", "fastapi-metrics-demo")
_APP_VERSION = os.getenv("APP_VERSION", "1.0.0")


@router.get("/health")
def health() -> dict:
    """Liveness probe. Returns 200 as long as the process is alive."""
    return {"status": "ok"}


@router.get("/readiness")
def readiness() -> dict:
    """Readiness probe with per-dependency checks.

    Extend `checks` to include database, cache, or downstream service pings.
    Raise `HTTPException(503, ...)` if any critical dependency is unhealthy so
    orchestrators know to stop routing traffic.
    """
    checks: dict[str, str] = {"app": "ok"}
    # Example additions:
    #   checks["database"] = "ok" if db.ping() else "fail"
    #   checks["cache"] = "ok" if redis.ping() else "fail"
    return {"status": "ready", "checks": checks}


@router.get("/info")
def info() -> dict:
    """App metadata + uptime — the human-readable counterpart to /metrics."""
    return {
        "name": _APP_NAME,
        "version": _APP_VERSION,
        "python": platform.python_version(),
        "platform": platform.platform(),
        "hostname": socket.gethostname(),
        "pid": os.getpid(),
        "uptime_seconds": round(time.time() - _STARTUP_TIME, 2),
    }
