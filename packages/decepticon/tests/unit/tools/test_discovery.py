"""Tests for the capability_search agent tool."""

from __future__ import annotations

import json

from decepticon.tools.bash import BASH_TOOLS
from decepticon.tools.discovery import CAPABILITY_DISCOVERY_TOOLS, capability_search


def _invoke(**kwargs: object) -> dict:
    return json.loads(capability_search.invoke(kwargs))


def test_capability_search_is_wired_into_bash_tools() -> None:
    # Every bash-running agent spreads BASH_TOOLS, so discovery ships with it.
    assert capability_search in BASH_TOOLS
    assert CAPABILITY_DISCOVERY_TOOLS == [capability_search]


def test_returns_structured_matches_with_reach() -> None:
    result = _invoke(query="secretsdump")
    assert result["count"] >= 1
    impacket = next(c for c in result["capabilities"] if c["id"] == "impacket")
    assert "impacket-secretsdump" in impacket["binaries"]
    assert impacket["reach"]
    assert impacket["risk"] == "intrusive"


def test_category_filter() -> None:
    result = _invoke(category="recon")
    assert result["count"] >= 1
    assert all(c["category"] == "recon" for c in result["capabilities"])


def test_sidecar_reach_is_not_bash() -> None:
    result = _invoke(query="ghidra", include_planned=True)
    ghidra = next(c for c in result["capabilities"] if c["id"] == "ghidra")
    assert ghidra["delivery"] == "sidecar"
    assert "NOT bash" in ghidra["reach"]


def test_no_match_returns_guidance_note() -> None:
    result = _invoke(query="definitely-not-a-real-tool-xyz")
    assert result["count"] == 0
    assert result["capabilities"] == []
    assert "note" in result


def test_invalid_max_risk_returns_error_and_valid_values() -> None:
    result = _invoke(max_risk="bogus")
    assert "error" in result
    assert "passive" in result["valid_max_risk"]


def test_planned_hidden_by_default() -> None:
    default = _invoke(query="volatility")
    planned = _invoke(query="volatility", include_planned=True)
    assert default["count"] == 0
    assert planned["count"] >= 1
