"""Secrets & CI/CD Exposure Agent — leaked credentials and build-chain exposure.

Hunts exposed secrets and CI/CD weaknesses that bug-bounty programs
reward: secrets in front-end JS bundles and source maps, exposed
``.git`` / ``.svn`` directories and ``.env`` / config files, leaked API
tokens and cloud keys, exposed CI artifacts and build logs, and public
CI/CD config (GitHub Actions / GitLab CI) revealing injectable workflow
or pipeline-poisoning surface. Complements the standard supply-chain
operator (which owns dependency / package-registry attacks).

Uses ``scan_secrets`` to extract and classify high-entropy credentials
from fetched JS / config, on top of the shared bash + web surface
(``.git`` reconstruction, source-map mining). Confirmed live credentials
are scope-checked and rendered as HackerOne / Bugcrowd submissions —
never used beyond proof needed for the report.
"""

from __future__ import annotations

from typing import Any

from decepticon.agents.bounty._common import make_bounty_agent
from decepticon.tools.research.secret_scanner import scan_secrets
from decepticon_core.plugin_loader import SubAgentSpec, is_bundle_enabled

_ROLE = "secrets_cicd"

# Extract + classify high-entropy secrets from fetched JS / config bundles.
_DOMAIN_TOOLS: list[Any] = [scan_secrets]

create_secrets_cicd_agent = make_bounty_agent(role=_ROLE, domain_tools=_DOMAIN_TOOLS)


# Module-level graph for LangGraph Platform (langgraph serve).
if is_bundle_enabled("bounty"):
    graph = create_secrets_cicd_agent()


SUBAGENT_SPEC = SubAgentSpec(
    name=_ROLE,
    description=(
        "Secrets & CI/CD exposure specialist. Use to find secrets in JS "
        "bundles / source maps, exposed .git / .env / config, leaked API & "
        "cloud tokens, and public CI/CD config (Actions / GitLab CI) with "
        "pipeline-poisoning surface. Extracts and classifies credentials "
        "with scan_secrets. Complements the supply-chain operator."
    ),
    factory=create_secrets_cicd_agent,
    parent_agents=("decepticon",),
    bundle="bounty",
    priority=69,
)
