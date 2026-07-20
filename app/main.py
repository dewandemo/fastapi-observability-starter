"""FastAPI application factory."""

import os

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from app.metrics import init_app_info
from app.routers import items, observability

APP_NAME = os.getenv("APP_NAME", "fastapi-metrics-demo")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    application = FastAPI(
        title=APP_NAME,
        version=APP_VERSION,
        description="A minimal FastAPI service with health, readiness, and Prometheus metrics.",
    )

    # Populate app_build_info metric
    init_app_info(name=APP_NAME, version=APP_VERSION)

    # HTTP metrics: auto request count, duration histogram, size, in-progress gauge.
    # /metrics, /health, /readiness are excluded to avoid noisy self-observation.
    Instrumentator(
        should_group_status_codes=False,
        should_ignore_untemplated=True,
        excluded_handlers=["/metrics", "/health", "/readiness"],
    ).instrument(application).expose(
        application, endpoint="/metrics", include_in_schema=False
    )

    # Routers
    application.include_router(observability.router)
    application.include_router(items.router)

    @application.get("/", tags=["meta"])
    def root() -> dict:
        return {
            "app": APP_NAME,
            "version": APP_VERSION,
            "docs": "/docs",
            "endpoints": [
                "/health",
                "/readiness",
                "/info",
                "/metrics",
                "/items",
            ],
        }

    return application


app = create_app()
