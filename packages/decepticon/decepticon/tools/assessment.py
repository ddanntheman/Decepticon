"""Expose artifact-only assessment coverage through the engagement's sandbox."""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import PurePosixPath
from typing import Annotated, Any, Literal
from urllib.parse import urlsplit

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from langgraph.prebuilt import InjectedState

from decepticon.backends.factory import build_sandbox_backend
from decepticon.backends.http_sandbox import HTTPSandbox
from decepticon.middleware.filesystem import (
    EngagementFilesystemBackend,
    _normalize_engagement_workspace,
)
from decepticon_core.types.roe import MachineEnforcement, ScopeRule, evaluate_target
from decepticon_core.utils.engagement_scope import is_valid_engagement_label


class AssessmentToolError(ValueError):
    """The assessment lacks a valid engagement context or artifact."""


def _context(state: dict[str, Any], config: RunnableConfig) -> tuple[HTTPSandbox, str, str]:
    configurable = config.get("configurable") or {}
    engagement = configurable.get("engagement_name", state.get("engagement_name"))
    workspace = configurable.get("workspace_path", state.get("workspace_path"))
    if not isinstance(engagement, str) or not is_valid_engagement_label(engagement):
        raise AssessmentToolError("A valid engagement must be set before using assessment tools")
    normalized = _normalize_engagement_workspace(workspace) if isinstance(workspace, str) else None
    if normalized is None:
        raise AssessmentToolError("A valid engagement workspace must be set")
    if (
        state.get("engagement_name") not in (None, engagement)
        and "workspace_path" not in configurable
    ):
        raise AssessmentToolError("Changed engagement requires an explicit matching workspace")
    return build_sandbox_backend(config), engagement, normalized


def _artifact(sandbox: HTTPSandbox, workspace: str, path: str) -> str:
    artifact = PurePosixPath(path)
    if not path or "\\" in path or ".." in artifact.parts:
        raise AssessmentToolError("Artifact paths must stay inside the engagement workspace")
    if artifact.is_absolute() and not (path == "/workspace" or path.startswith("/workspace/")):
        raise AssessmentToolError("Artifact paths must stay inside the engagement workspace")
    files = EngagementFilesystemBackend(sandbox, workspace).download_files([path])
    if len(files) != 1 or files[0].error or files[0].content is None:
        raise AssessmentToolError("Assessment artifact is unavailable in this engagement")
    content = files[0].content
    if len(content) > 16 * 1024 * 1024:
        raise AssessmentToolError(
            "Assessment artifacts must be at most 16 MiB; input was not truncated"
        )
    try:
        return content.decode("utf-8")
    except UnicodeError as exc:
        raise AssessmentToolError("Assessment artifacts must be UTF-8") from exc


def _document(sandbox: HTTPSandbox, workspace: str, path: str) -> dict[str, Any]:
    try:
        document = json.loads(_artifact(sandbox, workspace, path))
    except json.JSONDecodeError as exc:
        raise AssessmentToolError("Assessment plan and RoE must be valid JSON") from exc
    if not isinstance(document, dict):
        raise AssessmentToolError("Assessment plan and RoE must be JSON objects")
    return document


def _scope_rule(rule: ScopeRule) -> ScopeRule:
    pattern = rule.pattern
    if "://" in pattern:
        parts = urlsplit(pattern)
        if parts.path not in ("", "/") or parts.query or parts.fragment:
            raise AssessmentToolError(
                "Path-restricted scope requires an explicit assessment scope review"
            )
        pattern = parts.hostname or ""
    return ScopeRule(pattern=pattern, kind="auto")


def _rules(sandbox: HTTPSandbox, workspace: str) -> MachineEnforcement:
    roe = _document(sandbox, workspace, "plan/roe.json")
    machine = roe.get("machine_enforcement") or {}
    if not isinstance(machine, dict):
        raise AssessmentToolError("Invalid machine-enforcement scope")
    rules = MachineEnforcement.from_dict(
        {
            **machine,
            "in_scope": machine.get("in_scope") or roe.get("in_scope") or [],
            "out_of_scope": machine.get("out_of_scope") or roe.get("out_of_scope") or [],
        }
    )
    if not rules.in_scope:
        raise AssessmentToolError("Assessment requires an explicit RoE scope")
    return replace(
        rules,
        in_scope=tuple(_scope_rule(rule) for rule in rules.in_scope),
        out_of_scope=tuple(_scope_rule(rule) for rule in rules.out_of_scope),
    )


@tool(
    description="Initialize artifact-only coverage from operator-reviewed plan/assessment.json and plan/roe.json. The plan supplies profile, required_roles, available_roles and source_available; allowed hosts always come from RoE, never model arguments. This baseline is not a full ASVS audit."
)
def assessment_initialize(
    state: Annotated[dict[str, Any], InjectedState], config: RunnableConfig
) -> str:
    sandbox, engagement, workspace = _context(state, config)
    plan = _document(sandbox, workspace, "plan/assessment.json")
    rules = _rules(sandbox, workspace)
    payload = {
        key: plan[key]
        for key in ("profile", "required_roles", "available_roles", "source_available")
        if key in plan
    }
    payload.update(
        engagement_name=engagement,
        allowed_hosts=[rule.pattern for rule in rules.in_scope],
        denied_hosts=[rule.pattern for rule in rules.out_of_scope]
        + list(rules.effective_forbidden_destinations()),
    )
    return json.dumps(sandbox.assessment("initialize", payload, workspace_path=workspace))


@tool(
    description="Inspect persisted assessment coverage, inventory, gaps, or eligible next cases. Never probes a target. Follow next_offset until all pages are inspected; totals cover the full inventory."
)
def assessment_status(
    state: Annotated[dict[str, Any], InjectedState],
    config: RunnableConfig,
    view: Literal["report", "gaps", "inventory", "next"] = "gaps",
    offset: int = 0,
    limit: int = 50,
) -> str:
    sandbox, _, workspace = _context(state, config)
    return json.dumps(
        sandbox.assessment(view, {"offset": offset, "limit": limit}, workspace_path=workspace)
    )


@tool(
    description="Import all operations from an existing engagement artifact: openapi, traffic (HAR), observations, or source-status. No target requests. Content is checked against current RoE; credentials and parameter values are not inventory. Large inventories stay persisted and are viewed through assessment_status pagination."
)
def assessment_import(
    path: str,
    kind: Literal["openapi", "traffic", "observations", "source-status"],
    state: Annotated[dict[str, Any], InjectedState],
    config: RunnableConfig,
    base_url: str = "",
    source_id: str = "",
) -> str:
    from decepticon.assessment_import import prepare_import

    sandbox, _, workspace = _context(state, config)
    rules = _rules(sandbox, workspace)
    payload = prepare_import(kind, _artifact(sandbox, workspace, path), source_id or path, base_url)
    for operation in payload["operations"]:
        url = operation.get("url") or operation.get("base_url") or payload.get("base_url") or ""
        host = urlsplit(url).hostname
        if not host or not evaluate_target(host, rules).allow:
            raise AssessmentToolError("Imported operation is outside the current engagement scope")
    return json.dumps(sandbox.assessment("import", payload, workspace_path=workspace))


@tool(
    description="Evaluate one pending http.nosniff or http.hsts case against an existing captured-response JSON artifact. Never sends requests. Evidence must match the case URL and method and contain status_code, headers, captured_at, and source='capture'."
)
def assessment_check_headers(
    case_id: str,
    evidence_path: str,
    state: Annotated[dict[str, Any], InjectedState],
    config: RunnableConfig,
) -> str:
    sandbox, _, workspace = _context(state, config)
    return json.dumps(
        sandbox.assessment(
            "check_headers",
            {"case_id": case_id, "evidence_path": evidence_path},
            workspace_path=workspace,
        )
    )


@tool(
    description="Record an explicitly attested assessment result, not an independently verified finding. Pass/fail require existing workspace-relative evidence files, which are hashed. Missing access stays blocked, never not_applicable. Supply rationale for every disposition."
)
def assessment_record_result(
    case_id: str,
    status: Literal["pass", "fail", "blocked", "inconclusive", "not_applicable"],
    rationale: str,
    state: Annotated[dict[str, Any], InjectedState],
    config: RunnableConfig,
    evidence_paths: list[str] | None = None,
) -> str:
    sandbox, _, workspace = _context(state, config)
    return json.dumps(
        sandbox.assessment(
            "record",
            {
                "case_id": case_id,
                "status": status,
                "rationale": rationale,
                "evidence_paths": evidence_paths or [],
            },
            workspace_path=workspace,
        )
    )


ASSESSMENT_REVIEW_TOOLS = [assessment_status, assessment_check_headers, assessment_record_result]
ASSESSMENT_TOOLS = [assessment_initialize, assessment_import, *ASSESSMENT_REVIEW_TOOLS]
