from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from .model_registry import ROLES, model_env_key
from .provider import OpenAICompatibleProvider, ProviderError


SPECIALIST_SYSTEM = """You are one specialist inside RoboLab's multi-agent engineering system.
Analyze the user's robotics/embedded project ONLY from your assigned specialist role.
Return ONLY valid JSON with these keys:
assessment: string
findings: array of strings
recommendations: array of strings
risks: array of strings
confidence: number from 0 to 1
blocking: boolean

Rules:
- Do not invent datasheet facts, tool results, compilation results, simulations, or physical tests.
- State assumptions when hardware details are missing.
- Challenge the design rather than agreeing automatically.
- Keep recommendations compatible with the user's stated board/components when specified.
- Flag contradictions or missing information that another specialist should resolve.
- Refuse or flag unsafe high-voltage, explosive, weapon, or harmful-device work.
"""

SYNTHESIS_SYSTEM = """You are RoboLab Consensus, the final engineering integrator.
You receive a user request plus independent specialist findings from a 48-role review fleet.
Return ONLY valid JSON with these keys:
summary: string
architecture: array of strings
components: array of strings
connections: array of strings
firmware: string
validation: array of objects with ok:boolean, name:string, details:string
assumptions: array of strings
open_questions: array of strings
confidence: number from 0 to 1

Rules:
- Reconcile disagreements instead of blindly merging them.
- Prefer evidence and explicit constraints over majority vote.
- Never claim that code compiled, hardware was tested, or a circuit was electrically verified unless tool evidence is supplied.
- Preserve useful specialist warnings in validation.
- Include power/current/voltage/grounding checks for motors, servos, relays, pumps, batteries, and external supplies.
- Firmware should be complete enough to be a useful starting implementation when the board and behavior are sufficiently specified.
- Never generate instructions for weapons, explosives, or dangerous high-voltage systems.
"""


class EngineeringOrchestrator:
    """Runs the 48 specialist slots in parallel, then performs consensus synthesis."""

    def __init__(self, provider: OpenAICompatibleProvider | None = None) -> None:
        self.provider = provider or OpenAICompatibleProvider()
        self.max_concurrency = max(1, int(os.getenv("ROBOLAB_AGENT_CONCURRENCY", "8")))

    async def generate(self, prompt: str) -> dict[str, Any]:
        prompt = prompt.strip()
        if len(prompt) < 12:
            raise ValueError("Prompt is too short")

        blocked = self._risk_gate(prompt)
        if blocked:
            return self._safety_result(blocked)

        if not self.provider.available:
            return self._provider_unavailable("AI provider is not configured")

        specialist_results = await self._run_specialists(prompt)
        usable = [item for item in specialist_results if item.get("status") == "ok"]

        if not usable:
            return self._provider_unavailable("All 48 specialist model slots failed to return usable output")

        try:
            final = await self.provider.generate_json(
                system=SYNTHESIS_SYSTEM,
                user=(
                    "PROJECT REQUEST:\n"
                    + prompt
                    + "\n\nINDEPENDENT SPECIALIST REPORTS:\n"
                    + json.dumps(usable, ensure_ascii=False)
                ),
                model=os.getenv("ROBOLAB_SYNTHESIS_MODEL", self.provider.model),
                temperature=0.10,
            )
            result = self._normalize_final(final)
            result["source"] = "48-agent-consensus"
            result["agent_count"] = len(usable)
            result["agent_failures"] = len(specialist_results) - len(usable)
            result["agent_reports"] = specialist_results
            result["validation"] = self._augment_validation(prompt, result)
            return result
        except ProviderError as exc:
            return self._provider_unavailable(f"Consensus synthesis failed: {exc}")

    async def _run_specialists(self, prompt: str) -> list[dict[str, Any]]:
        semaphore = asyncio.Semaphore(self.max_concurrency)

        async def run(role) -> dict[str, Any]:
            async with semaphore:
                try:
                    model = os.getenv(model_env_key(role.id), self.provider.model).strip()
                    user = (
                        f"SPECIALIST ROLE: {role.name}\n"
                        f"DOMAIN: {role.domain}\n"
                        f"MISSION: {role.focus}\n\n"
                        f"PROJECT:\n{prompt}\n\n"
                        "Give an independent engineering review."
                    )
                    data = await self.provider.generate_json(
                        system=SPECIALIST_SYSTEM,
                        user=user,
                        model=model,
                        temperature=role.temperature,
                    )
                    return self._normalize_specialist(role.id, data)
                except Exception as exc:  # one failed specialist must not kill the fleet
                    return {
                        "role": role.id,
                        "status": "error",
                        "assessment": "Specialist unavailable.",
                        "findings": [],
                        "recommendations": [],
                        "risks": [str(exc)],
                        "confidence": 0.0,
                        "blocking": False,
                    }

        return list(await asyncio.gather(*(run(role) for role in ROLES)))

    @staticmethod
    def _risk_gate(prompt: str) -> str | None:
        text = prompt.lower()
        risky_terms = {
            "mains voltage": "Mains-voltage projects require qualified supervision and are not generated by this beta pipeline.",
            "high voltage": "High-voltage projects require additional expert safety review.",
            "explosive": "RoboLab does not generate explosive-device instructions.",
            "weapon": "RoboLab does not generate weapon-building instructions.",
            "bomb": "RoboLab does not generate explosive-device instructions.",
        }
        for term, message in risky_terms.items():
            if term in text:
                return message
        return None

    @staticmethod
    def _normalize_specialist(role_id: str, data: dict[str, Any]) -> dict[str, Any]:
        def strings(key: str) -> list[str]:
            raw = data.get(key, [])
            return [str(x).strip() for x in raw if str(x).strip()] if isinstance(raw, list) else []

        try:
            confidence = max(0.0, min(1.0, float(data.get("confidence", 0.0))))
        except (TypeError, ValueError):
            confidence = 0.0
        return {
            "role": role_id,
            "status": "ok",
            "assessment": str(data.get("assessment", "")).strip(),
            "findings": strings("findings"),
            "recommendations": strings("recommendations"),
            "risks": strings("risks"),
            "confidence": confidence,
            "blocking": bool(data.get("blocking", False)),
        }

    @staticmethod
    def _normalize_final(data: dict[str, Any]) -> dict[str, Any]:
        def strings(key: str) -> list[str]:
            raw = data.get(key, [])
            return [str(x).strip() for x in raw if str(x).strip()] if isinstance(raw, list) else []

        validation = data.get("validation", [])
        normalized_validation = []
        if isinstance(validation, list):
            for item in validation:
                if isinstance(item, dict):
                    normalized_validation.append({
                        "ok": bool(item.get("ok", False)),
                        "name": str(item.get("name", "Check")),
                        "details": str(item.get("details", "")),
                    })
        try:
            confidence = max(0.0, min(1.0, float(data.get("confidence", 0.0))))
        except (TypeError, ValueError):
            confidence = 0.0
        return {
            "summary": str(data.get("summary", "")),
            "architecture": strings("architecture"),
            "components": strings("components"),
            "connections": strings("connections"),
            "firmware": str(data.get("firmware", "")),
            "validation": normalized_validation,
            "assumptions": strings("assumptions"),
            "open_questions": strings("open_questions"),
            "confidence": confidence,
        }

    @staticmethod
    def _augment_validation(prompt: str, result: dict[str, Any]) -> list[dict[str, Any]]:
        checks = list(result.get("validation", []))
        text = prompt.lower()
        power_sensitive = any(term in text for term in ("motor", "servo", "relay", "battery", "pump", "stepper"))
        connections = " ".join(result.get("connections", [])).lower()

        checks.append({
            "ok": bool(result.get("components")),
            "name": "Component coverage",
            "details": f"{len(result.get('components', []))} component entries returned by consensus.",
        })
        checks.append({
            "ok": bool(result.get("firmware", "").strip()),
            "name": "Firmware presence",
            "details": "Firmware output is present." if result.get("firmware", "").strip() else "No firmware was returned.",
        })
        if power_sensitive:
            power_mentioned = any(token in connections for token in ("power", "supply", "current", "voltage", "ground"))
            checks.append({
                "ok": power_mentioned,
                "name": "Power-path review",
                "details": "Power considerations are represented in the generated connection plan." if power_mentioned else "Power-sensitive hardware needs explicit supply voltage, current and grounding analysis.",
            })
        if result.get("open_questions"):
            checks.append({
                "ok": False,
                "name": "Open engineering questions",
                "details": f"{len(result['open_questions'])} unresolved question(s) remain before a high-confidence build.",
            })
        return checks

    @staticmethod
    def _safety_result(message: str) -> dict[str, Any]:
        return {
            "summary": "This project is gated for safety review.",
            "architecture": [], "components": [], "connections": [], "firmware": "",
            "validation": [{"ok": False, "name": "Safety gate", "details": message}],
            "assumptions": [], "open_questions": [], "confidence": 0.0,
            "source": "safety-gate", "agent_count": 0, "agent_failures": 0, "agent_reports": [],
        }

    @staticmethod
    def _provider_unavailable(reason: str) -> dict[str, Any]:
        return {
            "summary": "The RoboLab backend is running, but the AI fleet is unavailable.",
            "architecture": [], "components": [], "connections": [], "firmware": "",
            "validation": [{"ok": False, "name": "AI fleet", "details": reason}],
            "assumptions": [], "open_questions": [], "confidence": 0.0,
            "source": "backend-no-provider", "agent_count": 0, "agent_failures": 48, "agent_reports": [],
        }
