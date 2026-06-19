"""API Security Agent — OWASP API Security Top 10.

Hunts the vulnerability classes that dominate modern bug-bounty payouts
and are largely invisible to generic scanners: BOLA / IDOR (object-level
authorization), broken function-level authorization (BFLA), broken
object property-level authorization (mass assignment / excessive data
exposure), broken authentication, unrestricted resource consumption, and
server-side request forgery surfaced through API parameters.

Works REST and JSON endpoints by enumerating objects and methods,
swapping identifiers and roles across authenticated sessions, and
diffing responses to prove unauthorized access. Driven by the shared
bash + web + payload surface; confirmed findings are scope-checked and
rendered as HackerOne / Bugcrowd submissions.
"""

from __future__ import annotations

from typing import Any

from decepticon.agents.bounty._common import make_bounty_agent
from decepticon_core.plugin_loader import SubAgentSpec, is_bundle_enabled

_ROLE = "api_security"

_DOMAIN_TOOLS: list[Any] = []

create_api_security_agent = make_bounty_agent(role=_ROLE, domain_tools=_DOMAIN_TOOLS)


# Module-level graph for LangGraph Platform (langgraph serve).
if is_bundle_enabled("bounty"):
    graph = create_api_security_agent()


SUBAGENT_SPEC = SubAgentSpec(
    name=_ROLE,
    description=(
        "API security specialist (OWASP API Top 10). Use against REST / JSON "
        "APIs to find BOLA/IDOR, broken function-level authorization (BFLA), "
        "mass assignment, excessive data exposure, and broken authentication "
        "by swapping object IDs and roles across sessions and diffing "
        "responses. High bug-bounty ROI; scanner-invisible."
    ),
    factory=create_api_security_agent,
    parent_agents=("decepticon",),
    bundle="bounty",
    priority=62,
)
