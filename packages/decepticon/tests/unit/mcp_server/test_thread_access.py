"""Selected-workspace isolation through the actual MCP protocol."""

from __future__ import annotations

from collections.abc import AsyncIterator
from pathlib import Path
from typing import Any

import pytest
from langgraph_sdk.schema import StreamPart
from mcp.server.fastmcp import FastMCP
from mcp.shared.memory import create_connected_server_and_client_session

from decepticon.mcp_server.config import ServerConfig
from decepticon.mcp_server.server import build_server


class _Threads:
    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace

    async def get_state(self, thread_id: str) -> dict[str, Any]:
        selected = thread_id in {"selected-thread", "misplaced-thread"}
        return {
            "values": {
                "engagement_name": "selected" if selected else "foreign",
                "workspace_path": str(self.workspace)
                if thread_id == "selected-thread"
                else "/foreign",
                "messages": [],
            }
        }

    async def search(self, *, limit: int, sort_by: str, sort_order: str) -> list[dict[str, Any]]:
        return [
            {"thread_id": "foreign-thread", "values": {"engagement_name": "foreign"}},
            {"thread_id": "misplaced-thread", "values": {"engagement_name": "selected"}},
            {"thread_id": "selected-thread", "values": {"engagement_name": "selected"}},
        ][:limit]


class _Runs:
    def __init__(self) -> None:
        self.cancelled: list[str] = []
        self.started: list[str] = []

    async def list(self, thread_id: str, *, limit: int) -> list[dict[str, Any]]:
        return [{"run_id": "run", "status": "running", "assistant_id": "soundwave"}]

    async def cancel(self, thread_id: str, run_id: str) -> None:
        self.cancelled.append(thread_id)

    async def create(
        self, thread_id: str, *, assistant_id: str, multitask_strategy: str, input: dict[str, Any]
    ) -> dict[str, str]:
        self.started.append(thread_id)
        return {"run_id": "run", "status": "pending"}

    async def join_stream(
        self, thread_id: str, run_id: str, *, stream_mode: list[str]
    ) -> AsyncIterator[StreamPart]:
        yield StreamPart("updates", {})


class _Client:
    def __init__(self, workspace: Path) -> None:
        self.threads = _Threads(workspace)
        self.runs = _Runs()


@pytest.fixture
def selected_client(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> _Client:
    monkeypatch.setenv("DECEPTICON_ENGAGEMENT", "selected")
    monkeypatch.setenv("DECEPTICON_ENGAGEMENT_WORKSPACE", str(tmp_path))
    return _Client(tmp_path)


def _server(client: _Client) -> FastMCP:
    return build_server(ServerConfig("http://test:2024", "soundwave", 10), client=client)


@pytest.mark.parametrize(
    ("tool", "arguments"),
    [
        ("decepticon_transcript", {}),
        ("decepticon_engagement_state", {}),
        ("decepticon_engagement_status", {}),
        ("decepticon_cancel_engagement", {}),
        ("decepticon_watch", {}),
        ("decepticon_send_message", {"message": "scope fixture"}),
    ],
)
@pytest.mark.parametrize("thread_id", ["foreign-thread", "misplaced-thread"])
async def test_selected_workspace_rejects_foreign_thread(
    tool: str, arguments: dict[str, str], thread_id: str, selected_client: _Client
) -> None:
    async with create_connected_server_and_client_session(_server(selected_client)) as session:
        response = await session.call_tool(tool, {"thread_id": thread_id, **arguments})
        assert response.isError and "does not belong" in str(response.content)


@pytest.mark.parametrize("thread_id", ["foreign-thread", "misplaced-thread"])
async def test_foreign_thread_is_not_cancelled(thread_id: str, selected_client: _Client) -> None:
    async with create_connected_server_and_client_session(_server(selected_client)) as session:
        await session.call_tool("decepticon_cancel_engagement", {"thread_id": thread_id})
        assert selected_client.runs.cancelled == []


@pytest.mark.parametrize("thread_id", ["foreign-thread", "misplaced-thread"])
async def test_foreign_thread_does_not_start_a_run(
    thread_id: str, selected_client: _Client
) -> None:
    async with create_connected_server_and_client_session(_server(selected_client)) as session:
        await session.call_tool(
            "decepticon_send_message", {"thread_id": thread_id, "message": "scope fixture"}
        )
        assert selected_client.runs.started == []


async def test_selected_workspace_list_excludes_foreign_threads(selected_client: _Client) -> None:
    async with create_connected_server_and_client_session(_server(selected_client)) as session:
        response = await session.call_tool("decepticon_list_engagements", {"limit": 1})
        rows = (response.structuredContent or {}).get("result", [])
        assert [row["thread_id"] for row in rows] == ["selected-thread"]
