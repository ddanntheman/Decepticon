"""Post-engagement retrospective analysis tools.

The retrospective agent runs at the end of every engagement to mine
``events.jsonl`` and the OPPLAN for failures, tool issues, access
problems, efficiency gaps, and coverage gaps.  It produces a structured
``retro/RETROSPECTIVE.md`` report with actionable improvement
requirements and a product-manager-ready backlog table.

Three tools:

1. ``retro_analyze_events`` -- statistical analysis of events.jsonl
2. ``retro_analyze_objectives`` -- OPPLAN gap analysis
3. ``retro_write_report`` -- writes retro/RETROSPECTIVE.md
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

from decepticon.tools.research._state import _json
from decepticon_core.utils.logging import get_logger

log = get_logger("research.retrospective")


# ── Helpers ──────────────────────────────────────────────────────────────


def _read_events(workspace: str) -> list[dict[str, Any]]:
    """Read events.jsonl from the workspace directory."""
    events_path = Path(workspace) / "events.jsonl"
    if not events_path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line in events_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            events.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return events


def _read_opplan(workspace: str) -> dict[str, Any] | None:
    """Read plan/opplan.json from the workspace directory."""
    opplan_path = Path(workspace) / "plan" / "opplan.json"
    if not opplan_path.exists():
        return None
    try:
        return json.loads(opplan_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None


def _analyze_agent_performance(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect agent-level failures from event data."""
    issues: list[dict[str, Any]] = []

    # Track per-agent metrics
    agent_tool_calls: dict[str, int] = Counter()
    agent_tool_errors: dict[str, int] = Counter()
    agent_llm_calls: dict[str, int] = Counter()
    agent_llm_errors: dict[str, int] = Counter()
    agent_first_event: dict[str, float] = {}
    agent_last_event: dict[str, float] = {}

    for ev in events:
        agent = ev.get("agent")
        if not agent:
            continue
        ts = ev.get("ts", 0.0)
        etype = ev.get("type", "")
        payload = ev.get("payload", {})

        if agent not in agent_first_event:
            agent_first_event[agent] = ts
        agent_last_event[agent] = ts

        if etype == "tool.call":
            agent_tool_calls[agent] += 1
        elif etype == "tool.result":
            if payload.get("status") == "error":
                agent_tool_errors[agent] += 1
        elif etype == "llm.call":
            agent_llm_calls[agent] += 1
        elif etype == "llm.response":
            if payload.get("error") or payload.get("status") == "error":
                agent_llm_errors[agent] += 1

    # Detect agents with 0 tool calls but significant runtime
    all_agents = set(agent_first_event.keys())
    for agent in all_agents:
        duration_s = agent_last_event.get(agent, 0) - agent_first_event.get(agent, 0)
        duration_m = duration_s / 60.0
        tool_calls = agent_tool_calls.get(agent, 0)
        tool_errors = agent_tool_errors.get(agent, 0)
        llm_calls = agent_llm_calls.get(agent, 0)
        llm_errors = agent_llm_errors.get(agent, 0)

        # Agent ran >5 minutes with 0 tool calls = likely stuck
        if tool_calls == 0 and duration_m > 5:
            issues.append(
                {
                    "category": "agent_failure",
                    "severity": "critical",
                    "title": f"Agent '{agent}' ran {duration_m:.0f}m with 0 tool calls",
                    "description": (
                        f"Agent '{agent}' was active for {duration_m:.1f} minutes "
                        f"but executed 0 tool calls. It made {llm_calls} LLM calls "
                        f"({llm_errors} errors). This indicates the agent was stuck "
                        f"in a retry loop — likely due to message-history corruption "
                        f"or middleware rejection causing every model call to fail."
                    ),
                    "evidence": {
                        "agent": agent,
                        "duration_minutes": round(duration_m, 1),
                        "tool_calls": tool_calls,
                        "llm_calls": llm_calls,
                        "llm_errors": llm_errors,
                    },
                    "recommended_fix": (
                        "Investigate middleware stack for this agent role. Check for "
                        "KG middleware rejection (kg-middleware-rejection), RoE "
                        "middleware rejection, or model fallback chain exhaustion. "
                        "The agent's message history likely contains an orphaned "
                        "ToolMessage that corrupts every subsequent model call."
                    ),
                    "effort": "medium",
                }
            )

        # Agent had >50% tool error rate
        if tool_calls > 3 and tool_errors / tool_calls > 0.5:
            issues.append(
                {
                    "category": "tool_failure",
                    "severity": "high",
                    "title": f"Agent '{agent}' had {tool_errors}/{tool_calls} tool failures ({tool_errors / tool_calls:.0%})",
                    "description": (
                        f"Agent '{agent}' executed {tool_calls} tool calls, but "
                        f"{tool_errors} returned errors ({tool_errors / tool_calls:.0%} "
                        f"failure rate). High tool failure rates indicate infrastructure "
                        f"issues, incorrect tool parameters, or access problems."
                    ),
                    "evidence": {
                        "agent": agent,
                        "tool_calls": tool_calls,
                        "tool_errors": tool_errors,
                        "error_rate": round(tool_errors / tool_calls, 2),
                    },
                    "recommended_fix": (
                        "Review the failing tool calls in events.jsonl for this agent. "
                        "Common causes: sandbox connectivity, missing credentials, "
                        "target unreachable, or middleware blocking legitimate calls."
                    ),
                    "effort": "small",
                }
            )

        # Agent had >50% LLM error rate
        if llm_calls > 3 and llm_errors / llm_calls > 0.5:
            issues.append(
                {
                    "category": "agent_failure",
                    "severity": "critical",
                    "title": f"Agent '{agent}' had {llm_errors}/{llm_calls} LLM call failures",
                    "description": (
                        f"Agent '{agent}' made {llm_calls} LLM calls, but "
                        f"{llm_errors} failed ({llm_errors / llm_calls:.0%} failure "
                        f"rate). This typically means message-history corruption "
                        f"(orphaned ToolMessage), model rate limiting, or the "
                        f"entire fallback chain was exhausted."
                    ),
                    "evidence": {
                        "agent": agent,
                        "llm_calls": llm_calls,
                        "llm_errors": llm_errors,
                        "error_rate": round(llm_errors / llm_calls, 2),
                    },
                    "recommended_fix": (
                        "Check for middleware-injected ToolMessages with fabricated "
                        "tool_call_ids. Verify the model fallback chain covers the "
                        "agent's tier. Check rate limit headers in error payloads."
                    ),
                    "effort": "medium",
                }
            )

    return issues


def _analyze_tool_patterns(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect tool-level failure patterns."""
    issues: list[dict[str, Any]] = []

    tool_calls: dict[str, int] = Counter()
    tool_errors: dict[str, int] = Counter()
    tool_error_messages: dict[str, list[str]] = defaultdict(list)

    for ev in events:
        etype = ev.get("type", "")
        payload = ev.get("payload", {})

        if etype == "tool.call":
            tool_name = payload.get("tool", "unknown")
            tool_calls[tool_name] += 1
        elif etype == "tool.result":
            tool_name = payload.get("tool", "unknown")
            if payload.get("status") == "error":
                tool_errors[tool_name] += 1
                error_msg = str(payload.get("error", ""))[:200]
                if error_msg:
                    tool_error_messages[tool_name].append(error_msg)

    # Tools that consistently fail
    for tool_name, error_count in tool_errors.items():
        total = tool_calls.get(tool_name, error_count)
        if error_count >= 3 and error_count / max(total, 1) > 0.5:
            sample_errors = tool_error_messages.get(tool_name, [])[:3]
            issues.append(
                {
                    "category": "tool_failure",
                    "severity": "high",
                    "title": f"Tool '{tool_name}' failed {error_count}/{total} times",
                    "description": (
                        f"Tool '{tool_name}' was called {total} times and "
                        f"returned errors {error_count} times "
                        f"({error_count / max(total, 1):.0%} failure rate)."
                    ),
                    "evidence": {
                        "tool": tool_name,
                        "total_calls": total,
                        "error_count": error_count,
                        "sample_errors": sample_errors,
                    },
                    "recommended_fix": (
                        f"Investigate why '{tool_name}' is failing. Check: "
                        f"(1) tool implementation for bugs, "
                        f"(2) required infrastructure/services are running, "
                        f"(3) credentials/access are configured. "
                        f"Sample errors: {'; '.join(sample_errors[:2]) if sample_errors else 'none captured'}"
                    ),
                    "effort": "medium",
                }
            )

    return issues


def _analyze_access_issues(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Detect access and infrastructure issues from event patterns."""
    issues: list[dict[str, Any]] = []

    access_error_keywords = [
        "connection refused",
        "timeout",
        "dns",
        "unreachable",
        "credential",
        "unauthorized",
        "forbidden",
        "403",
        "401",
        "rate limit",
        "quota",
        "sandbox",
        "middleware rejection",
        "kg-middleware-rejection",
        "roe",
        "out of scope",
    ]

    access_errors: dict[str, list[dict[str, Any]]] = defaultdict(list)

    for ev in events:
        payload = ev.get("payload", {})
        error_str = str(payload.get("error", "")).lower()
        content_str = str(payload.get("content", "")).lower()
        combined = error_str + " " + content_str

        for keyword in access_error_keywords:
            if keyword in combined:
                access_errors[keyword].append(
                    {
                        "ts": ev.get("ts"),
                        "type": ev.get("type"),
                        "agent": ev.get("agent"),
                        "tool": payload.get("tool", ""),
                    }
                )
                break

    for keyword, occurrences in access_errors.items():
        if len(occurrences) >= 2:
            agents_affected = list({o["agent"] for o in occurrences if o.get("agent")})
            issues.append(
                {
                    "category": "access_issue",
                    "severity": "high"
                    if keyword in ("credential", "unauthorized", "forbidden")
                    else "medium",
                    "title": f"Repeated '{keyword}' errors ({len(occurrences)} occurrences)",
                    "description": (
                        f"Detected {len(occurrences)} events containing '{keyword}' "
                        f"errors. Affected agents: {', '.join(agents_affected) or 'unknown'}."
                    ),
                    "evidence": {
                        "keyword": keyword,
                        "occurrence_count": len(occurrences),
                        "affected_agents": agents_affected,
                        "first_occurrence_ts": occurrences[0].get("ts"),
                        "last_occurrence_ts": occurrences[-1].get("ts"),
                    },
                    "recommended_fix": _access_fix_recommendation(keyword),
                    "effort": "small" if keyword in ("rate limit", "quota") else "medium",
                }
            )

    return issues


def _access_fix_recommendation(keyword: str) -> str:
    """Return specific fix guidance for access-pattern keywords."""
    recommendations = {
        "connection refused": "Verify the target service is running and the port is correct. Run the liveness probe before dispatching agents.",
        "timeout": "Check network connectivity to the target. Consider increasing timeout values or running the liveness probe first.",
        "dns": "Verify the target hostname resolves. Check DNS configuration and /etc/resolv.conf.",
        "unreachable": "Target host is unreachable. Verify network path, firewall rules, and VPN connectivity.",
        "credential": "Verify credentials are configured in the engagement workspace. Check .env files and secret storage.",
        "unauthorized": "Authentication is failing. Verify API keys, tokens, or session cookies are valid and not expired.",
        "forbidden": "Authorization is failing. The credentials may be valid but lack required permissions/scopes.",
        "rate limit": "The target or API provider is rate-limiting requests. Implement backoff or reduce concurrency.",
        "quota": "API quota exceeded. Check provider billing/quotas or switch to a different provider.",
        "sandbox": "Sandbox backend connectivity issue. Verify the sandbox container is running and responsive.",
        "kg-middleware-rejection": "KG middleware rejected a tool call due to missing kg_engagement scope. This is the known message-history corruption bug — verify PR #10 fix is applied.",
        "roe": "Rules of Engagement middleware blocked a call. Verify the RoE scope includes the target and the tool is permitted.",
        "out of scope": "An operation was blocked as out of scope. Review plan/roe.json and ensure all target surfaces are in-scope.",
    }
    return recommendations.get(
        keyword, f"Investigate '{keyword}' errors in events.jsonl for root cause."
    )


def _analyze_objective_gaps(objectives: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Analyze OPPLAN objectives for coverage and completion gaps."""
    issues: list[dict[str, Any]] = []

    status_counts: dict[str, int] = Counter()
    blocked_objectives: list[dict[str, Any]] = []
    failed_objectives: list[dict[str, Any]] = []

    for obj in objectives:
        status = obj.get("status", "unknown")
        status_counts[status] += 1

        if status == "blocked":
            blocked_objectives.append(obj)
        elif status == "failed":
            failed_objectives.append(obj)

    # Objectives that ended blocked
    for obj in blocked_objectives:
        obj_id = obj.get("id", "unknown")
        description = obj.get("description", "")
        reason = obj.get("reason", obj.get("notes", "no reason recorded"))
        issues.append(
            {
                "category": "coverage_gap",
                "severity": "medium",
                "title": f"Objective {obj_id} ended blocked: {description[:80]}",
                "description": (
                    f"Objective {obj_id} ('{description}') was blocked and "
                    f"never completed. Reason: {reason}"
                ),
                "evidence": {
                    "objective_id": obj_id,
                    "description": description,
                    "status": "blocked",
                    "reason": reason,
                },
                "recommended_fix": (
                    f"Investigate why {obj_id} was blocked. If it's an infrastructure "
                    f"issue (target unreachable, tool not available), fix the "
                    f"infrastructure. If it's a capability gap (no tool for this "
                    f"attack surface), build or configure the needed tooling."
                ),
                "effort": "medium",
            }
        )

    # Objectives that ended failed
    for obj in failed_objectives:
        obj_id = obj.get("id", "unknown")
        description = obj.get("description", "")
        reason = obj.get("reason", obj.get("notes", "no reason recorded"))
        issues.append(
            {
                "category": "coverage_gap",
                "severity": "high",
                "title": f"Objective {obj_id} failed: {description[:80]}",
                "description": (f"Objective {obj_id} ('{description}') failed. Reason: {reason}"),
                "evidence": {
                    "objective_id": obj_id,
                    "description": description,
                    "status": "failed",
                    "reason": reason,
                },
                "recommended_fix": (
                    f"Review why {obj_id} failed. Check agent dispatch logs "
                    f"for the assigned specialist. Determine if this was a "
                    f"tool/infrastructure issue vs a genuine negative finding."
                ),
                "effort": "medium",
            }
        )

    # Summary: high blocked/failed ratio
    total = len(objectives)
    blocked_failed = len(blocked_objectives) + len(failed_objectives)
    if total > 0 and blocked_failed / total > 0.5:
        issues.append(
            {
                "category": "efficiency_gap",
                "severity": "high",
                "title": f"{blocked_failed}/{total} objectives blocked or failed ({blocked_failed / total:.0%})",
                "description": (
                    "More than half of the engagement's objectives ended in a "
                    "non-success state. Status breakdown: "
                    + ", ".join(f"{s}={c}" for s, c in sorted(status_counts.items()))
                ),
                "evidence": {
                    "total_objectives": total,
                    "status_breakdown": dict(status_counts),
                    "blocked_count": len(blocked_objectives),
                    "failed_count": len(failed_objectives),
                },
                "recommended_fix": (
                    "Review engagement planning — were objectives realistic given "
                    "the available tooling and target surface? Consider whether "
                    "infrastructure issues (target unreachable, missing tools) "
                    "caused the high failure rate, or if the OPPLAN was overscoped."
                ),
                "effort": "small",
            }
        )

    return issues


# ── Tools ────────────────────────────────────────────────────────────────


@tool
def retro_analyze_events(workspace: str) -> str:
    """Analyze engagement events.jsonl for failures, errors, and patterns.

    Reads the engagement's event log and performs statistical analysis
    across three dimensions:

    1. **Agent performance** -- agents with 0 tool calls (stuck),
       high tool/LLM error rates, excessive runtime relative to output.
    2. **Tool patterns** -- tools that consistently fail, error messages.
    3. **Access / infra issues** -- connection errors, credential failures,
       middleware rejections, rate limiting.

    Returns a structured JSON analysis with detected issues and
    engagement-wide statistics.  Returns ``{"issue_count": 0}`` when
    the engagement had no detectable problems.

    Args:
        workspace: Path to the engagement workspace directory.
    """
    events = _read_events(workspace)
    if not events:
        return _json(
            {
                "status": "no_events",
                "issue_count": 0,
                "message": "No events.jsonl found or file is empty.",
            }
        )

    # Compute engagement-wide stats
    total_events = len(events)
    event_types: dict[str, int] = Counter(ev.get("type", "") for ev in events)
    agents_seen = list({ev.get("agent") for ev in events if ev.get("agent")})
    engagement_start = min((ev.get("ts", float("inf")) for ev in events), default=0)
    engagement_end = max((ev.get("ts", 0) for ev in events), default=0)
    duration_m = (engagement_end - engagement_start) / 60.0

    # Run analyses
    agent_issues = _analyze_agent_performance(events)
    tool_issues = _analyze_tool_patterns(events)
    access_issues = _analyze_access_issues(events)

    all_issues = agent_issues + tool_issues + access_issues

    # Sort by severity
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_issues.sort(key=lambda i: severity_order.get(i.get("severity", "low"), 4))

    return _json(
        {
            "status": "analyzed",
            "issue_count": len(all_issues),
            "engagement_stats": {
                "total_events": total_events,
                "event_type_counts": dict(event_types),
                "agents_observed": agents_seen,
                "duration_minutes": round(duration_m, 1),
                "tool_calls_total": event_types.get("tool.call", 0),
                "tool_errors_total": sum(
                    1
                    for ev in events
                    if ev.get("type") == "tool.result"
                    and ev.get("payload", {}).get("status") == "error"
                ),
                "llm_calls_total": event_types.get("llm.call", 0),
                "findings_created": event_types.get("finding.created", 0),
            },
            "issues": all_issues,
        }
    )


@tool
def retro_analyze_objectives(workspace: str) -> str:
    """Analyze OPPLAN objectives for coverage gaps and completion issues.

    Reads plan/opplan.json and identifies:

    1. Objectives that ended ``blocked`` -- what prevented completion?
    2. Objectives that ended ``failed`` -- what went wrong?
    3. Overall success rate -- high blocked/failed ratio indicates
       systemic issues.

    Returns structured JSON with detected issues.  Returns
    ``{"issue_count": 0}`` when all objectives completed successfully.

    Args:
        workspace: Path to the engagement workspace directory.
    """
    opplan = _read_opplan(workspace)
    if opplan is None:
        return _json(
            {
                "status": "no_opplan",
                "issue_count": 0,
                "message": "No plan/opplan.json found.",
            }
        )

    objectives = opplan.get("objectives", [])
    if not objectives:
        return _json(
            {
                "status": "no_objectives",
                "issue_count": 0,
                "message": "OPPLAN has no objectives.",
            }
        )

    issues = _analyze_objective_gaps(objectives)

    # Compute status summary
    status_counts: dict[str, int] = Counter(o.get("status", "unknown") for o in objectives)

    return _json(
        {
            "status": "analyzed",
            "issue_count": len(issues),
            "objective_summary": {
                "total": len(objectives),
                "status_breakdown": dict(status_counts),
                "engagement_name": opplan.get("engagement_name", ""),
            },
            "issues": issues,
        }
    )


@tool
def retro_write_report(workspace: str, report_markdown: str) -> str:
    """Write the retrospective report to retro/RETROSPECTIVE.md.

    Call this ONLY if issues were found (issue_count > 0).  The report
    should be in the standard retrospective format with an executive
    summary, numbered issues with evidence, and a product backlog table.

    Args:
        workspace: Path to the engagement workspace directory.
        report_markdown: The full markdown content for RETROSPECTIVE.md.
    """
    retro_dir = Path(workspace) / "retro"
    retro_dir.mkdir(parents=True, exist_ok=True)
    report_path = retro_dir / "RETROSPECTIVE.md"

    try:
        report_path.write_text(report_markdown, encoding="utf-8")
    except OSError as e:
        log.error("Failed to write retrospective report: %s", e)
        return _json({"error": f"Failed to write report: {e}"})

    return _json(
        {
            "written": True,
            "path": str(report_path),
            "size_bytes": report_path.stat().st_size,
        }
    )


# ── Public tool list ────────────────────────────────────────────────────

RETROSPECTIVE_TOOLS = [
    retro_analyze_events,
    retro_analyze_objectives,
    retro_write_report,
]
