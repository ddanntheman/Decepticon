"""API spec-driven security testing — OpenAPI/Swagger parsing + test gen.

Parses OpenAPI v2 (Swagger) and v3 specs to enumerate endpoints,
parameters, and auth schemes, then generates test matrices for
BOLA/BFLA, mass assignment, and boundary violations. Pure Python —
uses ``json`` / ``yaml``-compatible parsing (no external binary).
"""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

import httpx
from langchain_core.tools import tool

from decepticon_core.utils.logging import get_logger

log = get_logger("research.api_spec")

_TIMEOUT = 15.0


# ── Spec loading ─────────────────────────────────────────────────────────


def _load_spec(source: str) -> tuple[dict[str, Any] | None, str]:
    """Load an OpenAPI spec from a file path or URL. Returns (data, error)."""
    try:
        if source.startswith("http://") or source.startswith("https://"):
            with httpx.Client(
                timeout=_TIMEOUT,
                follow_redirects=True,
            ) as client:
                resp = client.get(source)
            if resp.status_code != 200:
                return None, f"HTTP {resp.status_code} fetching spec"
            text = resp.text
        else:
            path = Path(source)
            if not path.is_file():
                return None, f"File not found: {source}"
            text = path.read_text()

        # Try JSON first, then YAML-like
        try:
            return json.loads(text), ""
        except json.JSONDecodeError:
            # Minimal YAML-like parsing for common OpenAPI specs
            # (avoids adding pyyaml dependency)
            try:
                import yaml  # type: ignore[import-untyped]  # noqa: PLC0415

                return yaml.safe_load(text), ""
            except ImportError:
                return None, "Spec is YAML but pyyaml is not installed — convert to JSON"
    except (httpx.HTTPError, OSError) as exc:
        return None, str(exc)


# ── Spec parsing ─────────────────────────────────────────────────────────


def _extract_endpoints(spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract endpoints from an OpenAPI v2 or v3 spec."""
    endpoints: list[dict[str, Any]] = []
    paths = spec.get("paths") or {}
    base_path = spec.get("basePath", "")  # v2

    for path, methods in paths.items():
        if not isinstance(methods, dict):
            continue
        full_path = base_path + path if base_path else path
        for method, op in methods.items():
            if method.lower() in ("get", "post", "put", "patch", "delete", "head", "options"):
                if not isinstance(op, dict):
                    continue
                params = _extract_params(op, spec)
                auth = _extract_auth(op, spec)
                endpoints.append(
                    {
                        "path": full_path,
                        "method": method.upper(),
                        "operation_id": op.get("operationId", ""),
                        "summary": str(op.get("summary", ""))[:200],
                        "tags": op.get("tags", []),
                        "parameters": params,
                        "auth_required": auth,
                        "request_body": _extract_request_body(op),
                        "response_properties": _extract_response_properties(op, spec),
                    }
                )
    return endpoints


def _extract_params(op: dict[str, Any], spec: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract parameters from an operation."""
    params: list[dict[str, Any]] = []
    for p in op.get("parameters", []):
        if "$ref" in p:
            p = _resolve_ref(p["$ref"], spec) or p
        params.append(
            {
                "name": p.get("name", ""),
                "in": p.get("in", ""),
                "required": p.get("required", False),
                "type": _param_type(p),
            }
        )
    return params


def _param_type(p: dict[str, Any]) -> str:
    """Get parameter type string."""
    if "schema" in p:
        schema = p["schema"]
        return str(schema.get("type", schema.get("$ref", "object")))
    return str(p.get("type", "string"))


def _extract_auth(op: dict[str, Any], spec: dict[str, Any]) -> list[str]:
    """Extract auth requirements for an operation."""
    security = op.get("security") or spec.get("security") or []
    schemes: list[str] = []
    for sec in security:
        if isinstance(sec, dict):
            schemes.extend(sec.keys())
    return schemes


def _extract_request_body(op: dict[str, Any]) -> dict[str, Any] | None:
    """Extract request body schema (v3) or body parameter (v2)."""
    rb = op.get("requestBody")
    if rb and isinstance(rb, dict):
        content = rb.get("content", {})
        for ct, schema_info in content.items():
            if isinstance(schema_info, dict):
                return {
                    "content_type": ct,
                    "required": rb.get("required", False),
                    "schema_type": schema_info.get("schema", {}).get("type", "object"),
                    "properties": list(schema_info.get("schema", {}).get("properties", {}).keys())[
                        :20
                    ],
                }
    # v2 body param
    for p in op.get("parameters", []):
        if p.get("in") == "body" and "schema" in p:
            return {
                "content_type": "application/json",
                "required": p.get("required", False),
                "schema_type": p["schema"].get("type", "object"),
                "properties": list(p["schema"].get("properties", {}).keys())[:20],
            }
    return None


def _resolve_ref(ref: str, spec: dict[str, Any]) -> dict[str, Any] | None:
    """Resolve a $ref pointer (shallow, single-level)."""
    parts = ref.lstrip("#/").split("/")
    obj: Any = spec
    for part in parts:
        if isinstance(obj, dict):
            obj = obj.get(part)
        else:
            return None
    return obj if isinstance(obj, dict) else None


def _extract_response_properties(op: dict[str, Any], spec: dict[str, Any]) -> list[str]:
    """Extract response schema property names for the 200 response."""
    responses = op.get("responses", {})
    ok_resp = responses.get("200") or responses.get(200) or responses.get("201") or {}
    if "$ref" in ok_resp:
        ok_resp = _resolve_ref(ok_resp["$ref"], spec) or ok_resp
    # OpenAPI v3: content -> application/json -> schema -> properties
    content = ok_resp.get("content", {})
    for ct, media in content.items():
        if "json" in ct and isinstance(media, dict):
            schema = media.get("schema", {})
            if "$ref" in schema:
                schema = _resolve_ref(schema["$ref"], spec) or schema
            props = schema.get("properties", {})
            if props:
                return list(props.keys())[:30]
    # OpenAPI v2: schema -> properties
    schema = ok_resp.get("schema", {})
    if "$ref" in schema:
        schema = _resolve_ref(schema["$ref"], spec) or schema
    props = schema.get("properties", {})
    if props:
        return list(props.keys())[:30]
    return []


# ── Test matrix generation ───────────────────────────────────────────────


def _generate_bola_tests(endpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate BOLA/IDOR test cases for endpoints with ID parameters."""
    id_pattern = re.compile(r"(?i)(id|uuid|user_?id|account_?id|org_?id|resource_?id)")
    tests: list[dict[str, Any]] = []
    for ep in endpoints:
        id_params = [
            p for p in ep["parameters"] if id_pattern.search(p["name"]) or p.get("in") == "path"
        ]
        if id_params and ep["method"] in ("GET", "PUT", "PATCH", "DELETE"):
            tests.append(
                {
                    "test_type": "BOLA",
                    "endpoint": f"{ep['method']} {ep['path']}",
                    "id_params": [p["name"] for p in id_params],
                    "description": "Replace ID param with another user's ID to test horizontal privilege escalation",
                    "severity": "high",
                }
            )
    return tests


def _generate_mass_assignment_tests(endpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate mass assignment test cases for endpoints with request bodies."""
    sensitive_fields = re.compile(
        r"(?i)(role|admin|is_?admin|privilege|permission|balance|credit|status|verified|active)"
    )
    tests: list[dict[str, Any]] = []
    for ep in endpoints:
        if ep["method"] in ("POST", "PUT", "PATCH") and ep.get("request_body"):
            props = ep["request_body"].get("properties", [])
            sensitive = [p for p in props if sensitive_fields.search(p)]
            tests.append(
                {
                    "test_type": "mass_assignment",
                    "endpoint": f"{ep['method']} {ep['path']}",
                    "known_properties": props[:10],
                    "sensitive_properties_detected": sensitive,
                    "description": "Add extra fields (role, isAdmin, etc.) to request body",
                    "severity": "high" if sensitive else "medium",
                }
            )
    return tests


def _generate_auth_tests(endpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Generate auth bypass test cases."""
    tests: list[dict[str, Any]] = []
    for ep in endpoints:
        if ep["auth_required"]:
            tests.append(
                {
                    "test_type": "auth_bypass",
                    "endpoint": f"{ep['method']} {ep['path']}",
                    "auth_schemes": ep["auth_required"],
                    "description": "Send request without auth token to test enforcement",
                    "severity": "critical",
                }
            )
        if ep["method"] in ("PUT", "PATCH", "DELETE") and not ep["auth_required"]:
            tests.append(
                {
                    "test_type": "missing_auth",
                    "endpoint": f"{ep['method']} {ep['path']}",
                    "description": "State-changing endpoint has no auth requirement in spec",
                    "severity": "critical",
                }
            )
    return tests


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, default=str)


# ── @tool wrappers ───────────────────────────────────────────────────────


@tool
def api_parse_openapi(spec_source: str) -> str:
    """Parse an OpenAPI/Swagger spec and return all endpoints.

    Accepts a file path or URL to an OpenAPI v2 (Swagger) or v3 spec
    (JSON or YAML). Returns all endpoints with methods, parameters,
    auth requirements, and request body schemas. Use the output to
    understand the API surface before testing.
    """
    spec, error = _load_spec(spec_source)
    if spec is None:
        return _json({"error": "spec_load_failed", "detail": error})

    info = spec.get("info", {})
    endpoints = _extract_endpoints(spec)

    return _json(
        {
            "title": info.get("title", ""),
            "version": info.get("version", ""),
            "openapi_version": spec.get("openapi", spec.get("swagger", "")),
            "total_endpoints": len(endpoints),
            "endpoints": endpoints[:100],
        }
    )


@tool
def api_generate_test_matrix(spec_source: str) -> str:
    """Generate a security test matrix from an OpenAPI spec.

    Analyses the spec and generates test cases for:
    - **BOLA/IDOR**: endpoints with ID parameters → horizontal priv-esc
    - **Mass assignment**: endpoints with request bodies → extra field injection
    - **Auth bypass**: endpoints with/without auth → enforcement testing
    - **Missing auth**: state-changing endpoints without auth requirements

    Returns ranked test cases with descriptions and severity.
    """
    spec, error = _load_spec(spec_source)
    if spec is None:
        return _json({"error": "spec_load_failed", "detail": error})

    endpoints = _extract_endpoints(spec)
    bola = _generate_bola_tests(endpoints)
    mass_assign = _generate_mass_assignment_tests(endpoints)
    auth = _generate_auth_tests(endpoints)

    all_tests = bola + mass_assign + auth
    severity_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
    all_tests.sort(key=lambda x: severity_order.get(x.get("severity", "low"), 4))

    return _json(
        {
            "total_endpoints": len(endpoints),
            "total_tests": len(all_tests),
            "by_type": {
                "bola_idor": len(bola),
                "mass_assignment": len(mass_assign),
                "auth_bypass": len(auth),
            },
            "tests": all_tests[:100],
        }
    )


@tool
def api_detect_undocumented(base_url: str, spec_source: str) -> str:
    """Discover undocumented API fields by comparing live responses to spec.

    Fetches each GET endpoint in the spec and compares the response JSON
    keys against the documented schema properties. Extra fields may
    indicate mass-assignment vectors or information disclosure.
    """
    spec, error = _load_spec(spec_source)
    if spec is None:
        return _json({"error": "spec_load_failed", "detail": error})

    endpoints = _extract_endpoints(spec)
    get_endpoints = [ep for ep in endpoints if ep["method"] == "GET"][:20]

    findings: list[dict[str, Any]] = []
    try:
        with httpx.Client(
            timeout=_TIMEOUT,
            follow_redirects=True,
        ) as client:
            for ep in get_endpoints:
                path = ep["path"]
                # Skip paths with path params (we can't substitute)
                if "{" in path:
                    continue
                url = f"{base_url.rstrip('/')}{path}"
                try:
                    resp = client.get(url)
                    if resp.status_code == 200:
                        try:
                            body = resp.json()
                        except ValueError:
                            continue
                        if isinstance(body, dict):
                            live_keys = set(body.keys())
                            documented_keys = set(ep.get("response_properties", []))
                            extra = live_keys - documented_keys if documented_keys else live_keys
                            if extra:
                                findings.append(
                                    {
                                        "endpoint": f"GET {path}",
                                        "documented_fields": sorted(documented_keys),
                                        "undocumented_fields": sorted(extra),
                                        "severity": "medium",
                                    }
                                )
                except httpx.HTTPError:
                    continue
    except httpx.HTTPError as exc:
        return _json({"error": "request_failed", "detail": str(exc)})

    return _json(
        {
            "base_url": base_url,
            "endpoints_checked": len(get_endpoints),
            "endpoints_with_undocumented_fields": len(findings),
            "findings": findings,
        }
    )


API_SPEC_TOOLS = [api_parse_openapi, api_generate_test_matrix, api_detect_undocumented]
