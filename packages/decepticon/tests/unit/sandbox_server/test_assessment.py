from __future__ import annotations

import importlib
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

app_module = importlib.import_module("decepticon.sandbox_server.app")


def test_assessment_initialization_persists_in_the_selected_workspace(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SANDBOX_ROOT_DIR", str(tmp_path))
    monkeypatch.setattr(app_module, "_required_token", "assessment-fixture")
    client = TestClient(app_module.app)
    response = client.post(
        "/assessment",
        headers={"Authorization": "Bearer assessment-fixture"},
        json={
            "workspace_path": "/workspace/client-one",
            "action": "initialize",
            "payload": {
                "engagement_name": "client-one",
                "profile": "external",
                "allowed_hosts": ["app.example.test"],
            },
        },
    )
    assert response.status_code == 200
    assert (tmp_path / "client-one" / "assessment" / "coverage.sqlite3").is_file()
    report = client.post(
        "/assessment",
        headers={"Authorization": "Bearer assessment-fixture"},
        json={"workspace_path": "/workspace/client-one", "action": "report", "payload": {}},
    )
    assert report.status_code == 200
    assert report.json()["complete"] is False


@pytest.mark.parametrize(
    "workspace", ["", "/tmp", "/workspace/../elsewhere", "/workspace/a/../../b", "/workspace/a\\b"]
)
def test_assessment_rejects_invalid_workspaces_without_creating_state(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, workspace: str
) -> None:
    monkeypatch.setenv("SANDBOX_ROOT_DIR", str(tmp_path))
    monkeypatch.setattr(app_module, "_required_token", None)
    client = TestClient(app_module.app)
    response = client.post(
        "/assessment", json={"workspace_path": workspace, "action": "initialize", "payload": {}}
    )
    assert response.status_code == 422
    assert not list(tmp_path.iterdir())


def test_assessment_requires_the_daemon_bearer_token(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SANDBOX_ROOT_DIR", str(tmp_path))
    monkeypatch.setattr(app_module, "_required_token", "assessment-fixture")
    response = TestClient(app_module.app).post(
        "/assessment",
        json={"workspace_path": "/workspace/client-one", "action": "initialize", "payload": {}},
    )
    assert response.status_code == 401
    assert not list(tmp_path.iterdir())


def test_assessment_rejects_symlinked_workspace_escapes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root = tmp_path / "sandbox"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    (root / "client-one").symlink_to(outside, target_is_directory=True)
    monkeypatch.setenv("SANDBOX_ROOT_DIR", str(root))
    monkeypatch.setattr(app_module, "_required_token", None)
    response = TestClient(app_module.app).post(
        "/assessment",
        json={"workspace_path": "/workspace/client-one", "action": "initialize", "payload": {}},
    )
    assert response.status_code == 422
    assert not list(outside.iterdir())


def test_missing_assessment_is_an_error_not_an_empty_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("SANDBOX_ROOT_DIR", str(tmp_path))
    monkeypatch.setattr(app_module, "_required_token", None)
    response = TestClient(app_module.app).post(
        "/assessment", json={"workspace_path": "/workspace", "action": "report", "payload": {}}
    )
    assert response.status_code == 422
    assert not list(tmp_path.iterdir())


def test_assessment_endpoint_refuses_arbitrary_action_names(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(app_module, "_required_token", None)
    response = TestClient(app_module.app).post(
        "/assessment", json={"workspace_path": "/workspace", "action": "execute", "payload": {}}
    )
    assert response.status_code == 422
