"""Tests for /metrics — Prometheus exposition and custom series behavior."""


def _metric_value(text: str, series: str) -> float:
    """Extract the numeric value of a single-sample Prometheus series."""
    for line in text.splitlines():
        if line.startswith(f"{series} ") or line.startswith(f"{series}{{"):
            return float(line.rsplit(" ", 1)[-1])
    raise AssertionError(f"series not found in /metrics: {series!r}")


def test_metrics_endpoint_returns_prometheus_content_type(client):
    r = client.get("/metrics")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")


def test_metrics_exposes_custom_series(client):
    text = client.get("/metrics").text
    assert "app_items_total" in text
    assert "app_items_created_total" in text
    assert "app_build_info" in text


def test_metrics_exposes_process_and_python_series(client):
    text = client.get("/metrics").text
    # These come free from prometheus_client
    assert "process_cpu_seconds_total" in text
    assert "python_info" in text


def test_items_total_gauge_tracks_current_store(client):
    client.post("/items", json={"name": "a"})
    client.post("/items", json={"name": "b"})
    client.post("/items", json={"name": "c"})
    client.delete("/items/2")

    text = client.get("/metrics").text
    assert _metric_value(text, "app_items_total") == 2.0


def test_items_created_total_counter_only_increases(client):
    before = _metric_value(client.get("/metrics").text, "app_items_created_total")

    client.post("/items", json={"name": "a"})
    client.post("/items", json={"name": "b"})

    after = _metric_value(client.get("/metrics").text, "app_items_created_total")
    assert after == before + 2


def test_http_metrics_track_items_requests(client):
    # Excluded handlers (/health, /readiness, /metrics) won't appear; /items will.
    client.get("/items")
    client.post("/items", json={"name": "a"})
    client.get("/items/999")  # 404

    text = client.get("/metrics").text
    assert 'handler="/items"' in text
    assert 'handler="/items/{item_id}"' in text  # templated, not raw id
    assert 'status="404"' in text


def test_excluded_handlers_are_not_in_http_metrics(client):
    client.get("/health")
    client.get("/readiness")

    text = client.get("/metrics").text
    assert 'handler="/health"' not in text
    assert 'handler="/readiness"' not in text
