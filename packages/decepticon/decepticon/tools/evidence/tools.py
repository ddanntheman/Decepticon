"""LangChain ``@tool`` wrappers for the evidence package."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from langchain_core.tools import tool

from decepticon.tools.evidence.asciicast import (
    AsciicastExportError,
    export_asciicast,
    list_recordings,
)


def _json(data: Any) -> str:
    return json.dumps(data, indent=2, default=str, ensure_ascii=False)


def _workspace() -> Path:
    return Path(os.environ.get("DECEPTICON_ENGAGEMENT_WORKSPACE") or "/workspace")


def _evidence_dir() -> Path:
    return _workspace() / "evidence" / "recordings"


@tool
def export_session_asciicast(
    session_name: str,
    pipe_pane_log_path: str = "",
    title: str = "",
) -> str:
    """Convert a tmux session's pipe-pane log into an asciicast v2 (.cast) file.

    Produces ``<workspace>/evidence/recordings/<session_name>.cast`` plus a
    ``.cast.manifest.json`` sidecar. The asciicast file can be played back
    in any browser with asciinema-player and bundled into the engagement
    out-brief for client visibility into agent actions.

    Args:
        session_name: tmux session identifier used in the output filename.
        pipe_pane_log_path: explicit path to the pipe-pane log. When empty,
            falls back to ``<workspace>/.tmux-logs/<session_name>.log`` (the
            default location used by the sandbox FastAPI daemon).
        title: optional asciicast title; defaults to ``"Decepticon session <name>"``.
    """
    log_path = (
        Path(pipe_pane_log_path)
        if pipe_pane_log_path
        else _workspace() / ".tmux-logs" / f"{session_name}.log"
    )
    out_dir = _evidence_dir()
    out_path = out_dir / f"{session_name}.cast"
    try:
        manifest = export_asciicast(
            log_path=log_path,
            output_path=out_path,
            session_name=session_name,
            title=title,
        )
    except AsciicastExportError as exc:
        return _json({"error": str(exc)})
    return _json({"status": "exported", **manifest})


@tool
def list_session_recordings() -> str:
    """List all asciicast recordings captured for the current engagement.

    Reads ``<workspace>/evidence/recordings/*.cast.manifest.json`` and
    returns the parsed manifests. Use this before generating the
    engagement out-brief to know which recordings are available for embedding.
    """
    manifests = list_recordings(_evidence_dir())
    return _json({"count": len(manifests), "recordings": manifests})


EVIDENCE_TOOLS = [export_session_asciicast, list_session_recordings]
