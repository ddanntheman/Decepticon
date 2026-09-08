"""Registry-backed capability discovery for agents.

Turns the machine-readable Kali capability registry
(:mod:`decepticon_core.capabilities`) into an agent-callable search tool
so a specialist can ask "what tool do I have for X, and how do I reach
it?" BEFORE hand-rolling a curl/Python loop or assuming a tool is
missing. Read-only: it inspects the static registry, runs no commands,
and touches no engagement state — so it carries no RoE/sandbox context
and is safe for every role.
"""

from __future__ import annotations

import json

from langchain_core.tools import tool

from decepticon_core.capabilities import RiskTier, reach_instruction, search_capabilities

# Cap the payload so a broad query can't flood the model's context. The
# response tells the agent how many matched and how to narrow.
_RESULT_CAP = 40


@tool(
    description=(
        "Search the Kali capability registry for security tools that are actually "
        "installed/available on this platform, and learn how to reach each one "
        "(run in bash, activate a profile, use a sidecar's dedicated tools, or "
        "pip-install). Use this BEFORE writing a custom script or concluding a "
        "tool is unavailable. Optional filters (AND-combined): query (free-text "
        "over id/description/binaries/category), category (e.g. recon, web, ad, "
        "reversing, credentials), phase (MITRE tactic id e.g. TA0006), max_risk "
        "(passive|bounded_active|intrusive|high_impact|hardware), include_planned "
        "(also show not-yet-installed tools). Returns JSON; runs no commands."
    )
)
def capability_search(
    query: str = "",
    category: str = "",
    phase: str = "",
    max_risk: str = "",
    include_planned: bool = False,
) -> str:
    try:
        caps = search_capabilities(
            query=query,
            category=category,
            phase=phase,
            max_risk=max_risk or None,
            include_planned=include_planned,
        )
    except ValueError as exc:
        return json.dumps(
            {
                "error": str(exc),
                "valid_max_risk": [tier.name.lower() for tier in RiskTier],
            }
        )

    total = len(caps)
    shown = caps[:_RESULT_CAP]
    payload: dict[str, object] = {
        "count": total,
        "returned": len(shown),
        "capabilities": [
            {
                "id": cap.id,
                "category": cap.category,
                "binaries": list(cap.binaries),
                "delivery": cap.delivery,
                "reach": reach_instruction(cap),
                "risk": cap.risk_tier.name.lower(),
                "phases": list(cap.phases),
                "lifecycle": cap.lifecycle.value,
                "description": cap.description,
            }
            for cap in shown
        ],
    }
    if total == 0:
        payload["note"] = (
            "No matching supported/preview capabilities. Try include_planned=true, "
            "a broader query, or consult the <KALI_ENVIRONMENT> prompt block."
        )
    elif total > len(shown):
        payload["note"] = (
            f"{total} matches; showing first {len(shown)}. Narrow with "
            "category/phase/max_risk or a more specific query."
        )
    return json.dumps(payload)


CAPABILITY_DISCOVERY_TOOLS = [capability_search]

__all__ = ["CAPABILITY_DISCOVERY_TOOLS", "capability_search"]
