"""SkillogyMiddleware — Phase 1a Brain Anatomy thin wrapper around the
skillogy service (Neo4j-backed). Replaces the file-system-backed
SkillsMiddleware in agents wired with ``DECEPTICON_SKILL_BACKEND=
skillogy_brain``.

Agent tool surface (Phase 1a, four tools)
-----------------------------------------
- ``load_skill(name_or_path)`` — fetch the full body + frontmatter of
  one ``:Skill`` node. Accepts either a unique ``name`` or the
  canonical ``/skills/.../SKILL.md`` path.
- ``find_skill(query?, subdomain?, mitre_id?, tag?, tactic_id?,
  limit=20)`` — relationship-aware discovery. AND-combined filters.
  Returns each match's name, path, subdomain, description, plus the
  matched MITRE IDs and tags so the agent sees *why* the skill came
  back.
- ``traverse(from_path, edge_types?, depth=2)`` — explicit graph
  walking from a Skill seed along a whitelisted edge set.
- ``run_cypher_read(query, params?)`` — read-only Cypher escape hatch.
  Server enforces ``default_access_mode=READ`` + a write-keyword
  denylist (CREATE, MERGE, SET, DELETE, …).

Transitional architecture note
------------------------------
Phase 1a service-architecture pivot (spec v0.2.1) says this middleware
should be a *thin REST/gRPC client* of the standalone skillogy
container, not own a Bolt connection of its own. This first cut wires
a direct ``Neo4jBackend`` to deliver the four tools end-to-end against
the live graph; a follow-on PR within Phase 1a swaps it for
``RestSkillogyClient`` once the REST endpoints are rewritten on top of
``Neo4jBackend``. The tool surface seen by the agent is identical
either way.
"""

from __future__ import annotations

import json
import logging
import os
from typing import Any

from langchain.agents.middleware import AgentMiddleware
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.tools import tool
from typing_extensions import override

log = logging.getLogger(__name__)


_DEFAULT_NEO4J_URI = "bolt://neo4j:7687"
_DEFAULT_NEO4J_USER = "neo4j"
_DEFAULT_NEO4J_PASSWORD = "decepticon-graph"  # nosec B105 — local-dev default; production overrides via env
_POLICY_PROMPT = (
    "\n\n[Skillogy access]\n"
    "Skills live in a Neo4j knowledge graph. You have four tools:\n"
    "- ``load_skill(name_or_path)`` — fetch one SKILL.md body. Accept either a unique\n"
    "  name (e.g. 'kerberoasting') or the canonical /skills/.../SKILL.md path.\n"
    "- ``find_skill(query?, subdomain?, mitre_id?, tag?, tactic_id?, limit=20)`` —\n"
    "  relationship-aware discovery. Filters AND-combine. Returns each hit's name,\n"
    "  path, subdomain, description, matched_mitre, matched_tags so you see why it matched.\n"
    "- ``traverse(from_path, edge_types?, depth=2)`` — variable-length BFS from a Skill\n"
    "  seed along the relationship whitelist (IN_PHASE, IMPLEMENTS, TAGGED, BELONGS_TO,\n"
    "  RELATED_TO, HAS_TECHNIQUE, HAS_SUBTECHNIQUE).\n"
    "- ``run_cypher_read(query, params?)`` — read-only Cypher escape hatch when the\n"
    "  curated tools don't fit. Write-mode keywords (CREATE/MERGE/SET/DELETE/…) are\n"
    "  refused server-side.\n"
    "Workflow: prefer find_skill to narrow candidates, then load_skill on the chosen\n"
    "match. Use traverse for 'what relates to this' questions and run_cypher_read for\n"
    "anything more bespoke.\n"
)


def _resolve_neo4j_uri() -> str:
    return os.environ.get("DECEPTICON_SKILLOGY_NEO4J_URI", _DEFAULT_NEO4J_URI)


def _resolve_neo4j_user() -> str:
    return os.environ.get("DECEPTICON_SKILLOGY_NEO4J_USER", _DEFAULT_NEO4J_USER)


def _resolve_neo4j_password() -> str:
    return os.environ.get("DECEPTICON_SKILLOGY_NEO4J_PASSWORD", _DEFAULT_NEO4J_PASSWORD)


def _is_enabled() -> bool:
    if os.environ.get("DECEPTICON_USE_SKILLOGY", "").strip().lower() in {"1", "true", "yes", "on"}:
        return True
    return os.environ.get("DECEPTICON_SKILL_BACKEND", "").strip().lower() == "skillogy_brain"


def _backend_factory():
    from decepticon.skillogy.server.neo4j_backend import Neo4jBackend  # noqa: PLC0415

    return Neo4jBackend(
        uri=_resolve_neo4j_uri(),
        user=_resolve_neo4j_user(),
        password=_resolve_neo4j_password(),
    )


def _make_load_skill_tool(backend):
    @tool
    def load_skill(name_or_path: str) -> str:
        """Fetch one SKILL.md's body + metadata from the skillogy graph.

        Accepts either a unique frontmatter ``name`` (e.g. 'kerberoasting')
        or the canonical ``/skills/.../SKILL.md`` path. Returns the full
        body + frontmatter fields as JSON.
        """
        try:
            if name_or_path.startswith("/skills/"):
                props = backend.load_skill(name_or_path)
            else:
                # Resolve by name via a single-shot find. This keeps
                # load_skill's signature agent-friendly; the agent does
                # not need to remember paths.
                hits = backend.find_skill(query=name_or_path, limit=10)
                exact = [h for h in hits if h.get("name") == name_or_path]
                if not exact:
                    return json.dumps(
                        {"error": f"no Skill with name or path matching {name_or_path!r}"}
                    )
                props = backend.load_skill(exact[0]["path"])
            if props is None:
                return json.dumps({"error": f"no Skill at path {name_or_path!r}"})
            return json.dumps(props, ensure_ascii=False, default=str)
        except Exception as exc:  # noqa: BLE001 — surface as ToolMessage payload
            return json.dumps({"error": f"load_skill failed: {exc!r}"})

    return load_skill


def _make_find_skill_tool(backend):
    @tool
    def find_skill(
        query: str | None = None,
        subdomain: str | None = None,
        mitre_id: str | None = None,
        tag: str | None = None,
        tactic_id: str | None = None,
        limit: int = 20,
    ) -> str:
        """Relationship-aware skill discovery in the skillogy graph.

        Filters AND-combine. Pass at least one. ``query`` substring-matches
        name/description/triggers. ``subdomain`` follows IN_PHASE.
        ``mitre_id`` follows IMPLEMENTS to a Technique. ``tag`` follows
        TAGGED. ``tactic_id`` (e.g. 'TA0001' for Initial Access) ladders
        via IMPLEMENTS → HAS_TECHNIQUE. Returns each hit's name, path,
        subdomain, description, matched_mitre, matched_tags.
        """
        try:
            hits = backend.find_skill(
                query=query,
                subdomain=subdomain,
                mitre_id=mitre_id,
                tag=tag,
                tactic_id=tactic_id,
                limit=limit,
            )
            return json.dumps({"count": len(hits), "hits": hits}, ensure_ascii=False, default=str)
        except ValueError as exc:
            return json.dumps({"error": str(exc)})
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"error": f"find_skill failed: {exc!r}"})

    return find_skill


def _make_traverse_tool(backend):
    @tool
    def traverse(
        from_path: str,
        edge_types: list[str] | None = None,
        depth: int = 2,
    ) -> str:
        """Variable-length BFS from a Skill seed along the relationship whitelist.

        ``from_path`` is the canonical /skills/.../SKILL.md path of the
        starting Skill. ``edge_types`` defaults to the spec-§5.7.2
        whitelist (IN_PHASE, IMPLEMENTS, TAGGED, BELONGS_TO, RELATED_TO,
        HAS_TECHNIQUE, HAS_SUBTECHNIQUE). ``depth`` ≤ 5. Returns each
        neighbour's label, key, depth, and the edge-type chain that
        connected it.
        """
        try:
            rows = backend.traverse(from_path, edge_types=edge_types, depth=depth)
            return json.dumps({"count": len(rows), "rows": rows}, ensure_ascii=False, default=str)
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"error": f"traverse failed: {exc!r}"})

    return traverse


def _make_run_cypher_read_tool(backend):
    @tool
    def run_cypher_read(query: str, params: dict[str, Any] | None = None) -> str:
        """Read-only Cypher escape hatch.

        Use this only when the curated tools (``load_skill``, ``find_skill``,
        ``traverse``) cannot express the question. Server enforces
        ``default_access_mode='READ'`` on the Bolt session and applies a
        write-keyword denylist before the query reaches Neo4j. Rows are
        capped server-side.
        """
        try:
            rows = backend.run_cypher_read(query, params or {})
            return json.dumps({"count": len(rows), "rows": rows}, ensure_ascii=False, default=str)
        except Exception as exc:  # noqa: BLE001
            return json.dumps({"error": f"run_cypher_read failed: {exc!r}"})

    return run_cypher_read


class SkillogyMiddleware(AgentMiddleware):
    """Wire the agent to the skillogy knowledge graph (Neo4j).

    Activation: set ``DECEPTICON_SKILL_BACKEND=skillogy_brain`` (preferred)
    or the legacy ``DECEPTICON_USE_SKILLOGY=1``. The agent factory's
    ``maybe_install_skillogy`` swaps ``SkillsMiddleware`` for this class.
    """

    def __init__(
        self,
        *,
        backend: Any = None,
        append_policy_to_system: bool = True,
    ) -> None:
        super().__init__()
        self._backend = backend or _backend_factory()
        self._append_policy = append_policy_to_system
        self.tools = [
            _make_load_skill_tool(self._backend),
            _make_find_skill_tool(self._backend),
            _make_traverse_tool(self._backend),
            _make_run_cypher_read_tool(self._backend),
        ]

    @classmethod
    def from_env(cls) -> SkillogyMiddleware:
        return cls()

    @override
    def wrap_model_call(self, request, handler):
        return handler(self._inject(request))

    @override
    async def awrap_model_call(self, request, handler):
        return await handler(self._inject(request))

    def _inject(self, request):
        if not self._append_policy:
            return request
        if request.system_message is not None:
            new_content = [
                *request.system_message.content_blocks,
                {"type": "text", "text": _POLICY_PROMPT},
            ]
        else:
            new_content = [{"type": "text", "text": _POLICY_PROMPT}]
        new_system = SystemMessage(content=new_content)
        return request.override(system_message=new_system)

    @override
    def wrap_tool_call(self, request, handler) -> ToolMessage:
        return handler(request)

    @override
    async def awrap_tool_call(self, request, handler) -> ToolMessage:
        return await handler(request)


def maybe_install_skillogy(middleware_stack: list[Any]) -> list[Any]:
    """Substitute ``SkillogyMiddleware`` for ``SkillsMiddleware`` when the
    backend flag is set. Idempotent; swap-only (does not append).
    """
    if not _is_enabled():
        return middleware_stack
    try:
        from decepticon.middleware.skills import SkillsMiddleware  # noqa: PLC0415
    except ImportError:
        return middleware_stack
    out: list[Any] = []
    for mw in middleware_stack:
        if isinstance(mw, SkillsMiddleware):
            out.append(SkillogyMiddleware.from_env())
        else:
            out.append(mw)
    return out
