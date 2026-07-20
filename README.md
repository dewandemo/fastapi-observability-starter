# fastapi-metrics-demo

FastAPI service with health, readiness, info, and Prometheus metrics endpoints.
Structured like a real project: routers separated by concern, custom metrics
isolated, tests covering every endpoint.

## Layout

```
fastapi-metrics-demo/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI app factory
│   ├── metrics.py              # Custom Prometheus metrics
│   └── routers/
│       ├── __init__.py
│       ├── observability.py    # /health, /readiness, /info
│       └── items.py            # /items CRUD
├── tests/
│   ├── __init__.py
│   ├── conftest.py             # Shared fixtures (TestClient + state reset)
│   ├── test_observability.py
│   ├── test_items.py
│   └── test_metrics.py
├── Dockerfile
├── .dockerignore
├── pyproject.toml              # pytest config
├── requirements.txt
├── requirements-dev.txt
└── README.md
```

## Endpoints

| Method | Path             | Purpose                                              |
| ------ | ---------------- | ---------------------------------------------------- |
| GET    | `/`              | Root — lists endpoints                               |
| GET    | `/health`        | Liveness probe                                       |
| GET    | `/readiness`     | Readiness probe with per-dependency `checks`         |
| GET    | `/info`          | Name, version, uptime, Python/platform info, PID     |
| GET    | `/metrics`       | Prometheus exposition (auto HTTP + custom metrics)   |
| GET    | `/items`         | List all items                                       |
| POST   | `/items`         | Create an item                                       |
| GET    | `/items/{id}`    | Fetch by ID                                          |
| DELETE | `/items/{id}`    | Remove by ID                                         |
| GET    | `/docs`          | Swagger UI (built into FastAPI)                      |
| GET    | `/redoc`         | ReDoc alternative                                    |

## Run locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8080
```

## Run tests

```bash
pip install -r requirements-dev.txt
pytest
```

Coverage: 5 tests for observability, 11 for CRUD, 7 for metrics = 23 tests.

## Run in Docker

```bash
docker build -t fastapi-metrics-demo .
docker run --rm -p 8080:8080 fastapi-metrics-demo
```

The container runs as a non-root user and includes a `HEALTHCHECK` that hits
`/health` every 30 seconds.

## Metrics reference

### HTTP metrics (auto)
`prometheus-fastapi-instrumentator` adds:

| Metric                            | Type      | Labels                          |
| --------------------------------- | --------- | ------------------------------- |
| `http_requests_total`             | counter   | method, handler, status         |
| `http_request_duration_seconds`   | histogram | method, handler, status         |
| `http_request_size_bytes`         | summary   | method, handler                 |
| `http_response_size_bytes`        | summary   | method, handler                 |
| `http_requests_inprogress`        | gauge     | method, handler                 |

`/metrics`, `/health`, and `/readiness` are excluded from these to avoid
noisy self-observation.

### Custom metrics (defined in `app/metrics.py`)

| Metric                       | Type    | What it tells you                            |
| ---------------------------- | ------- | -------------------------------------------- |
| `app_items_total`            | gauge   | Current item count in the in-memory store    |
| `app_items_created_total`    | counter | Cumulative items created since process start |
| `app_build_info{...}`        | info    | Build labels: name, version, python_version  |

### Process metrics (from `prometheus_client`)
Standard `process_*` and `python_*` series: CPU time, RSS memory, open FDs,
GC stats, thread count, Python version.

## Extending readiness

`/readiness` should return 503 when a critical dependency is unhealthy:

```python
from fastapi import HTTPException, status

@router.get("/readiness")
def readiness():
    checks = {"app": "ok"}
    try:
        db.ping()
        checks["database"] = "ok"
    except Exception:
        checks["database"] = "fail"
        raise HTTPException(
            status.HTTP_503_SERVICE_UNAVAILABLE,
            {"status": "not ready", "checks": checks},
        )
    return {"status": "ready", "checks": checks}
```

Kubernetes / ECS will stop routing traffic to instances that fail readiness
while keeping them alive so they can recover.

## Configuration

Env vars read at startup:

- `APP_NAME`    — default `fastapi-metrics-demo`
- `APP_VERSION` — default `1.0.0`; bake this at build time in CI so `/info`
  and `app_build_info{version=...}` reflect the actual release.
