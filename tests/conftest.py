"""Shared pytest fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.routers.items import reset_state


@pytest.fixture()
def client() -> TestClient:
    """A `TestClient` with the in-memory store reset before each test."""
    reset_state()
    return TestClient(app)
