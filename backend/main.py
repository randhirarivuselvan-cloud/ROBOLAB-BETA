from __future__ import annotations

import os
import time
from collections import defaultdict

from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from ai.model_registry import ROLES
from ai.orchestrator import EngineeringOrchestrator
from premium import export_bundle, plan_payload, premium_view, public_plans

app = FastAPI(title="RoboLab Backend", version="0.3.0")
orchestrator = EngineeringOrchestrator()

# Android clients need cross-origin access when the backend is hosted separately.
allowed_origins = [item.strip() for item in os.getenv("ROBOLAB_CORS_ORIGINS", "*").split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# Lightweight single-instance abuse protection. Use a real shared rate limiter
# (Redis/API gateway) when horizontally scaling beyond one Render instance.
_RATE_WINDOW = max(1, int(os.getenv("ROBOLAB_RATE_WINDOW_SECONDS", "60")))
_RATE_LIMIT = max(1, int(os.getenv("ROBOLAB_RATE_LIMIT", "20")))
_rate_state: dict[str, list[float]] = defaultdict(list)


@app.middleware("http")
async def rate_limit(request: Request, call_next):
    if request.url.path.startswith("/api/v1/projects/") and request.method == "POST":
        client = request.client.host if request.client else "unknown"
        now = time.monotonic()
        recent = [stamp for stamp in _rate_state[client] if now - stamp < _RATE_WINDOW]
        if len(recent) >= _RATE_LIMIT:
            return Response("Rate limit exceeded. Try again shortly.", status_code=429)
        recent.append(now)
        _rate_state[client] = recent
    return await call_next(request)


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=12, max_length=8000)


class ExportRequest(BaseModel):
    result: dict


@app.get("/healthz")
async def healthz() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/readyz")
async def readyz() -> dict[str, object]:
    return {
        "status": "ready" if orchestrator.provider.available else "degraded",
        "ai_provider_configured": orchestrator.provider.available,
    }


@app.get("/api/status")
async def status() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "robolab-backend",
        "version": app.version,
        "ai_fleet": {
            "configured_slots": len(ROLES),
            "active_slots": len(ROLES) if orchestrator.provider.available else 0,
            "architecture": "48 specialist agents + consensus synthesis",
        },
        "premium": plan_payload(),
    }


@app.get("/api/v1/plans")
async def plans() -> dict[str, object]:
    return {"plans": public_plans(), "active_beta_plan": plan_payload()}


@app.post("/api/v1/projects/generate")
async def generate_project(request: GenerateRequest):
    try:
        result = await orchestrator.generate(request.prompt)
        return premium_view(result)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.post("/api/v1/projects/export")
async def export_project(request: ExportRequest) -> Response:
    # Export is server-side so future authenticated billing can gate it without
    # shipping provider credentials to the Android client.
    if plan_payload()["id"] not in {"pro", "studio"}:
        raise HTTPException(status_code=402, detail="Project export is a RoboLab Pro feature.")
    return Response(
        content=export_bundle(request.result),
        media_type="application/json",
        headers={"Content-Disposition": "attachment; filename=robolab-project.json"},
    )
