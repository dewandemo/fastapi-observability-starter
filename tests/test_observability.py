"""Tests for /health, /readiness, /info, and the root endpoint."""


def test_health_returns_ok(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_readiness_reports_app_check(client):
    r = client.get("/readiness")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ready"
    assert body["checks"]["app"] == "ok"


def test_info_includes_all_expected_fields(client):
    r = client.get("/info")
    assert r.status_code == 200
    body = r.json()
    for field in (
        "name",
        "version",
        "python",
        "platform",
        "hostname",
        "pid",
        "uptime_seconds",
    ):
        assert field in body, f"missing field: {field}"


def test_info_uptime_is_non_negative_number(client):
    body = client.get("/info").json()
    assert isinstance(body["uptime_seconds"], (int, float))
    assert body["uptime_seconds"] >= 0


def test_root_lists_all_endpoints(client):
    body = client.get("/").json()
    for path in ("/health", "/readiness", "/info", "/metrics", "/items"):
        assert path in body["endpoints"]
