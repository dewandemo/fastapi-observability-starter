"""Landing page — Captain Canary greets visitors and shows deploy metadata."""

import os
import socket
from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["landing"])


def _format_deployed_at() -> str:
    """Format Harness's unix-ms pipeline.startTs into a human-readable UTC string."""
    raw = os.getenv("HARNESS_DEPLOYED_AT", "")
    if not raw:
        return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    try:
        ts_ms = int(raw)
        return datetime.fromtimestamp(ts_ms / 1000, tz=timezone.utc).strftime(
            "%Y-%m-%d %H:%M UTC"
        )
    except (ValueError, TypeError):
        return raw


def _meta() -> dict:
    return {
        "pipeline_id": os.getenv("HARNESS_PIPELINE_ID", "local-dev"),
        "execution_seq": os.getenv("HARNESS_EXECUTION_SEQ", "0"),
        "image_tag": os.getenv("HARNESS_IMAGE_TAG", "untagged"),
        "deployed_at": _format_deployed_at(),
        "execution_url": os.getenv("HARNESS_EXECUTION_URL", "#"),
        "hostname": socket.gethostname(),
    }


@router.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing() -> HTMLResponse:
    html = _HTML
    for key, value in _meta().items():
        html = html.replace("{{" + key + "}}", str(value))
    return HTMLResponse(content=html)


_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Deployed via Harness · Captain Canary</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600;700&family=Geist+Mono:wght@400;500&display=swap" rel="stylesheet">
<link href="https://api.fontshare.com/v2/css?f[]=cal-sans@1&display=swap" rel="stylesheet">
<style>
  * { box-sizing: border-box; }
  :root {
    --harness-1: #EFFBFF;
    --harness-3: #A3E9FF;
    --harness-4: #3DC7F6;
    --harness-5: #00ADE4;
    --harness-8: #004BA4;
    --harness-9: #0A3364;
    --harness-10: #07182B;
  }
  html, body { height: 100%; }
  body {
    margin: 0;
    font-family: 'Geist', -apple-system, BlinkMacSystemFont, system-ui, sans-serif;
    background:
      radial-gradient(1400px 700px at 15% -10%, rgba(0,173,228,0.18), transparent 60%),
      radial-gradient(900px 500px at 100% 100%, rgba(0,75,164,0.22), transparent 60%),
      linear-gradient(160deg, var(--harness-10) 0%, var(--harness-9) 100%);
    color: var(--harness-1);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 2rem;
    line-height: 1.5;
    -webkit-font-smoothing: antialiased;
  }
  .card {
    background: rgba(10, 51, 100, 0.35);
    border: 1px solid rgba(61, 199, 246, 0.15);
    border-radius: 24px;
    padding: 2.5rem 3rem;
    max-width: 940px;
    width: 100%;
    box-shadow:
      0 20px 60px rgba(0, 0, 0, 0.4),
      inset 0 1px 0 rgba(255, 255, 255, 0.04);
    backdrop-filter: blur(20px);
    display: grid;
    grid-template-columns: 280px 1fr;
    gap: 2.5rem;
    align-items: center;
  }
  .canary { width: 100%; max-width: 280px; height: auto; display: block; }
  .content { min-width: 0; }
  .logo { margin-bottom: 1.25rem; display: inline-flex; }
  .logo img { height: 24px; width: auto; display: block; }
  .badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    background: rgba(0, 173, 228, 0.12);
    border: 1px solid rgba(0, 173, 228, 0.3);
    color: var(--harness-3);
    padding: 0.3rem 0.8rem;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 500;
    letter-spacing: 0.02em;
    margin-bottom: 1rem;
  }
  .badge::before {
    content: '';
    width: 6px; height: 6px;
    background: var(--harness-4);
    border-radius: 50%;
    box-shadow: 0 0 0 3px rgba(61, 199, 246, 0.25);
  }
  h1 {
    font-family: 'Cal Sans', 'Geist', sans-serif;
    margin: 0 0 0.6rem;
    font-size: 2rem;
    font-weight: 400;
    letter-spacing: -0.015em;
    line-height: 1.15;
  }
  h1 .accent { color: var(--harness-4); }
  p.lead {
    margin: 0 0 1.5rem;
    color: #9db2d4;
    font-size: 0.98rem;
    max-width: 50ch;
  }
  dl {
    display: grid;
    grid-template-columns: max-content 1fr;
    gap: 0.6rem 1.5rem;
    margin: 0 0 1.75rem;
    padding: 1.25rem 1.5rem;
    background: rgba(7, 24, 43, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.05);
    border-radius: 12px;
  }
  dt {
    color: #7b8cb0;
    font-size: 0.7rem;
    font-weight: 500;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    align-self: center;
  }
  dd {
    margin: 0;
    font-family: 'Geist Mono', ui-monospace, monospace;
    font-size: 0.85rem;
    color: var(--harness-1);
    word-break: break-all;
  }
  .links { display: flex; flex-wrap: wrap; gap: 0.5rem; }
  .links a {
    display: inline-flex;
    align-items: center;
    padding: 0.5rem 0.9rem;
    background: rgba(0, 173, 228, 0.08);
    border: 1px solid rgba(0, 173, 228, 0.25);
    color: var(--harness-3);
    border-radius: 8px;
    text-decoration: none;
    font-family: 'Geist Mono', ui-monospace, monospace;
    font-size: 0.82rem;
    font-weight: 500;
    transition: all 0.15s ease;
  }
  .links a:hover {
    background: rgba(0, 173, 228, 0.15);
    color: var(--harness-1);
    border-color: rgba(0, 173, 228, 0.5);
  }
  @media (max-width: 720px) {
    .card {
      grid-template-columns: 1fr;
      padding: 2rem 1.5rem;
      gap: 1.5rem;
      text-align: center;
    }
    .canary { max-width: 200px; margin: 0 auto; }
    h1 { font-size: 1.6rem; }
    p.lead { margin-left: auto; margin-right: auto; }
    dl { grid-template-columns: 1fr; gap: 0.4rem; text-align: left; }
    dt { margin-top: 0.5rem; }
    .links { justify-content: center; }
    .logo, .badge { align-self: flex-start; }
  }
</style>
</head>
<body>
<main class="card">
  <img class="canary" src="/static/captain-canary.png" alt="Captain Canary, the Harness mascot">
  <div class="content">
    <div class="logo"><img src="/static/harness-logo.jpeg" alt="Harness"></div>
    <div class="badge">Deployment successful</div>
    <h1>Hey there! Shipped by a <span class="accent">Harness</span> pipeline.</h1>
    <p class="lead">This FastAPI service was just rolled out to Amazon ECS by a Harness Continuous Delivery pipeline.</p>
    <dl>
      <dt>Pipeline</dt><dd>{{pipeline_id}}</dd>
      <dt>Execution</dt><dd>#{{execution_seq}}</dd>
      <dt>Image tag</dt><dd>{{image_tag}}</dd>
      <dt>Deployed</dt><dd>{{deployed_at}}</dd>
      <dt>Container</dt><dd>{{hostname}}</dd>
    </dl>
    <div class="links">
      <a href="/docs">/docs</a>
      <a href="/health">/health</a>
      <a href="/readiness">/readiness</a>
      <a href="/info">/info</a>
      <a href="/metrics">/metrics</a>
      <a href="/items">/items</a>
    </div>
  </div>
</main>
</body>
</html>
"""
