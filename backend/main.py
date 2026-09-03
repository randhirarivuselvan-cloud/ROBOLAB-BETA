from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from ai.orchestrator import EngineeringOrchestrator

app = FastAPI(title="RoboLab Backend", version="0.1.0")
orchestrator = EngineeringOrchestrator()


class GenerateRequest(BaseModel):
    prompt: str = Field(min_length=12, max_length=8000)


@app.get("/api/status")
async def status() -> dict[str, str]:
    return {"status": "ok", "service": "robolab-backend"}


@app.post("/api/v1/projects/generate")
async def generate_project(request: GenerateRequest):
    try:
        return await orchestrator.generate(request.prompt)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
