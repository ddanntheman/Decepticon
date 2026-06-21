"""Unit tests for API spec-driven security testing tools.

No live HTTP calls — httpx is monkeypatched.
"""

from __future__ import annotations

import json
from pathlib import Path

from decepticon.tools.research import api_spec as asp

_SAMPLE_SPEC_V3 = {
    "openapi": "3.0.0",
    "info": {"title": "Test API", "version": "1.0.0"},
    "paths": {
        "/users/{userId}": {
            "get": {
                "operationId": "getUser",
                "summary": "Get a user by ID",
                "parameters": [
                    {
                        "name": "userId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                ],
                "security": [{"bearerAuth": []}],
            },
            "put": {
                "operationId": "updateUser",
                "summary": "Update user profile",
                "parameters": [
                    {
                        "name": "userId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                ],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "name": {"type": "string"},
                                    "email": {"type": "string"},
                                    "role": {"type": "string"},
                                    "isAdmin": {"type": "boolean"},
                                },
                            }
                        }
                    },
                },
                "security": [{"bearerAuth": []}],
            },
            "delete": {
                "operationId": "deleteUser",
                "summary": "Delete user",
                "parameters": [
                    {
                        "name": "userId",
                        "in": "path",
                        "required": True,
                        "schema": {"type": "string"},
                    },
                ],
            },
        },
        "/public/health": {
            "get": {
                "operationId": "healthCheck",
                "summary": "Health check",
            },
        },
    },
    "components": {
        "securitySchemes": {
            "bearerAuth": {"type": "http", "scheme": "bearer"},
        }
    },
}


class TestSpecLoading:
    def test_load_json_file(self, tmp_path: Path) -> None:
        f = tmp_path / "spec.json"
        f.write_text(json.dumps(_SAMPLE_SPEC_V3))
        data, err = asp._load_spec(str(f))
        assert data is not None
        assert err == ""
        assert data["openapi"] == "3.0.0"

    def test_file_not_found(self) -> None:
        data, err = asp._load_spec("/nonexistent/spec.json")
        assert data is None
        assert "not found" in err.lower()


class TestExtractEndpoints:
    def test_extracts_all_endpoints(self) -> None:
        endpoints = asp._extract_endpoints(_SAMPLE_SPEC_V3)
        assert len(endpoints) == 4  # GET, PUT, DELETE /users/{userId} + GET /public/health
        methods = {ep["method"] for ep in endpoints}
        assert "GET" in methods
        assert "PUT" in methods
        assert "DELETE" in methods

    def test_extracts_params(self) -> None:
        endpoints = asp._extract_endpoints(_SAMPLE_SPEC_V3)
        get_user = next(ep for ep in endpoints if ep["operation_id"] == "getUser")
        assert len(get_user["parameters"]) == 1
        assert get_user["parameters"][0]["name"] == "userId"

    def test_extracts_auth(self) -> None:
        endpoints = asp._extract_endpoints(_SAMPLE_SPEC_V3)
        get_user = next(ep for ep in endpoints if ep["operation_id"] == "getUser")
        assert "bearerAuth" in get_user["auth_required"]

    def test_extracts_request_body(self) -> None:
        endpoints = asp._extract_endpoints(_SAMPLE_SPEC_V3)
        update_user = next(ep for ep in endpoints if ep["operation_id"] == "updateUser")
        assert update_user["request_body"] is not None
        assert "role" in update_user["request_body"]["properties"]
        assert "isAdmin" in update_user["request_body"]["properties"]


class TestBolaTests:
    def test_generates_bola_for_id_params(self) -> None:
        endpoints = asp._extract_endpoints(_SAMPLE_SPEC_V3)
        bola = asp._generate_bola_tests(endpoints)
        assert len(bola) >= 1
        assert all(t["test_type"] == "BOLA" for t in bola)


class TestMassAssignmentTests:
    def test_detects_sensitive_fields(self) -> None:
        endpoints = asp._extract_endpoints(_SAMPLE_SPEC_V3)
        mass = asp._generate_mass_assignment_tests(endpoints)
        assert len(mass) >= 1
        update_test = next(t for t in mass if "PUT /users" in str(t.get("endpoint", "")))
        assert "role" in update_test["sensitive_properties_detected"]
        assert "isAdmin" in update_test["sensitive_properties_detected"]


class TestAuthTests:
    def test_detects_missing_auth(self) -> None:
        endpoints = asp._extract_endpoints(_SAMPLE_SPEC_V3)
        auth = asp._generate_auth_tests(endpoints)
        # DELETE /users/{userId} has no security spec
        missing_auth = [t for t in auth if t["test_type"] == "missing_auth"]
        assert len(missing_auth) >= 1


class TestApiParseOpenapi:
    def test_parses_spec(self, tmp_path: Path) -> None:
        f = tmp_path / "spec.json"
        f.write_text(json.dumps(_SAMPLE_SPEC_V3))
        result = json.loads(asp.api_parse_openapi.invoke({"spec_source": str(f)}))
        assert result["title"] == "Test API"
        assert result["total_endpoints"] == 4

    def test_bad_file(self) -> None:
        result = json.loads(asp.api_parse_openapi.invoke({"spec_source": "/nonexistent"}))
        assert result["error"] == "spec_load_failed"


class TestApiGenerateTestMatrix:
    def test_generates_tests(self, tmp_path: Path) -> None:
        f = tmp_path / "spec.json"
        f.write_text(json.dumps(_SAMPLE_SPEC_V3))
        result = json.loads(asp.api_generate_test_matrix.invoke({"spec_source": str(f)}))
        assert result["total_tests"] > 0
        assert result["by_type"]["bola_idor"] >= 1
        assert result["by_type"]["mass_assignment"] >= 1
        # Tests should be sorted by severity
        severities = [t["severity"] for t in result["tests"]]
        sev_order = {"critical": 0, "high": 1, "medium": 2, "low": 3}
        assert all(
            sev_order.get(a, 5) <= sev_order.get(b, 5) for a, b in zip(severities, severities[1:])
        )
