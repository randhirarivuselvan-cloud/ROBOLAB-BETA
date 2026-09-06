from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ai.model_registry import ROLES
from ai.orchestrator import EngineeringOrchestrator

app = FastAPI(title="RoboLab Backend", version="0.2.0")
orchestrator = EngineeringOrchestrator()


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=12, max_length=8000)


@app.get("/api/status")
async def status() -> dict[str, object]:
    return {
        "status": "ok",
        "service": "robolab-backend",
        "ai_fleet": {
            "configured_slots": len(ROLES),
            "active_slots": len(ROLES) if orchestrator.provider.available else 0,
            "architecture": "48 specialist agents + consensus synthesis",
        },
    }


@app.post("/api/v1/projects/generate")
async def generate_project(request: GenerateRequest):
    try:
        return await orchestrator.generate(request.prompt)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
