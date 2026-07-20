# syntax=docker/dockerfile:1.7
# ---- builder ----
FROM python:3.12-slim AS builder

WORKDIR /build
COPY requirements.txt .
RUN pip install --no-cache-dir --target=/deps -r requirements.txt

# ---- runtime ----
FROM python:3.12-slim

WORKDIR /app
COPY --from=builder /deps /deps
COPY app/ ./app/

ENV PYTHONPATH=/deps \
    PYTHONUNBUFFERED=1 \
    PORT=8080

# Non-root user
RUN useradd --create-home --uid 1000 appuser \
    && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request,sys; \
sys.exit(0) if urllib.request.urlopen('http://localhost:8080/health',timeout=2).status==200 else sys.exit(1)"

CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
