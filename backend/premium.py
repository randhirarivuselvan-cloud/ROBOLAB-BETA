from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Plan:
    id: str
    name: str
    monthly_inr: int | None
    yearly_inr: int | None
    max_projects: int | None
    features: tuple[str, ...]


PLANS: tuple[Plan, ...] = (
    Plan(
        id="free",
        name="RoboLab Free",
        monthly_inr=0,
        yearly_inr=0,
        max_projects=5,
        features=("core_builder", "basic_circuit", "basic_code", "basic_validation"),
    ),
    Plan(
        id="pro",
        name="RoboLab Pro",
        monthly_inr=99,
        yearly_inr=799,
        max_projects=None,
        features=(
            "full_48_agent_fleet",
            "consensus_engine",
            "specialist_reports",
            "advanced_validation",
            "power_analysis",
            "cad_ready_specs",
            "simulation_test_plans",
            "firmware_review",
            "project_export",
            "priority_generation",
        ),
    ),
    Plan(
        id="studio",
        name="RoboLab Studio",
        monthly_inr=299,
        yearly_inr=2399,
        max_projects=None,
        features=(
            "everything_pro",
            "team_workspaces",
            "shared_projects",
            "advanced_model_routing",
            "audit_history",
        ),
    ),
)

PLAN_BY_ID = {plan.id: plan for plan in PLANS}


def default_plan() -> str:
    """Server-side beta entitlement. Keep this server controlled until billing/auth is connected."""
    configured = os.getenv("ROBOLAB_DEFAULT_PLAN", "free").strip().lower()
    return configured if configured in PLAN_BY_ID else "free"


def plan_payload(plan_id: str | None = None) -> dict[str, Any]:
    plan = PLAN_BY_ID.get(plan_id or default_plan(), PLAN_BY_ID["free"])
    return asdict(plan) | {"features": list(plan.features)}


def is_premium(plan_id: str | None = None) -> bool:
    return (plan_id or default_plan()) in {"pro", "studio"}


def public_plans() -> list[dict[str, Any]]:
    return [asdict(plan) | {"features": list(plan.features)} for plan in PLANS]


def premium_view(result: dict[str, Any], plan_id: str | None = None) -> dict[str, Any]:
    """Add entitlement-aware metadata without exposing provider secrets."""
    plan = plan_id or default_plan()
    payload = dict(result)
    payload["plan"] = plan_payload(plan)
    if not is_premium(plan):
        payload.pop("agent_reports", None)
        payload["premium"] = {"enabled": False, "upgrade_required": True}
    else:
        payload["premium"] = {
            "enabled": True,
            "upgrade_required": False,
            "features_used": [
                "full_48_agent_fleet",
                "consensus_engine",
                "advanced_validation",
                "specialist_reports",
            ],
        }
    return payload


def export_bundle(result: dict[str, Any]) -> bytes:
    """Create a portable JSON project bundle for premium export/download flows."""
    bundle = {
        "format": "robolab-project-bundle",
        "version": 1,
        "project": result,
    }
    return json.dumps(bundle, ensure_ascii=False, indent=2).encode("utf-8")
