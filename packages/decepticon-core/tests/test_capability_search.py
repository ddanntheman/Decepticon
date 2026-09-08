"""Tests for the registry search + reach helpers used by agent discovery."""

from __future__ import annotations

import pytest

from decepticon_core.capabilities import (
    BINARY_TO_CAPABILITY,
    CAPABILITY_REGISTRY,
    Lifecycle,
    RiskTier,
    reach_instruction,
    search_capabilities,
)


def test_search_defaults_to_supported_and_preview_only() -> None:
    results = search_capabilities()
    assert results
    assert all(c.lifecycle in (Lifecycle.SUPPORTED, Lifecycle.PREVIEW) for c in results)


def test_include_planned_surfaces_planned_capabilities() -> None:
    without = search_capabilities()
    with_planned = search_capabilities(include_planned=True)
    assert len(with_planned) > len(without)
    assert any(c.lifecycle is Lifecycle.PLANNED for c in with_planned)


def test_query_matches_binary_and_description() -> None:
    by_binary = search_capabilities(query="secretsdump")
    assert any(c.id == "impacket" for c in by_binary)
    # Free-text also hits the description text, not just ids/binaries.
    assert search_capabilities(query="port scanner")


def test_category_filter_is_exact() -> None:
    recon = search_capabilities(category="recon")
    assert recon
    assert all(c.category == "recon" for c in recon)
    assert search_capabilities(category="RECON") == recon


def test_phase_filter_matches_mitre_tactic() -> None:
    creds = search_capabilities(phase="TA0006")
    assert creds
    assert all("TA0006" in c.phases for c in creds)


def test_max_risk_excludes_riskier_tools() -> None:
    passive = search_capabilities(max_risk="passive")
    assert passive
    assert all(c.risk_tier is RiskTier.PASSIVE for c in passive)
    # A higher ceiling is a superset.
    intrusive = search_capabilities(max_risk="intrusive")
    assert len(intrusive) >= len(passive)
    assert all(c.risk_tier.value <= RiskTier.INTRUSIVE.value for c in intrusive)


def test_unknown_max_risk_raises() -> None:
    with pytest.raises(ValueError, match="unknown max_risk"):
        search_capabilities(max_risk="nope")


def test_reach_instruction_reflects_delivery() -> None:
    assert "run it directly" in reach_instruction(BINARY_TO_CAPABILITY["nmap"])
    assert "sidecar" in reach_instruction(BINARY_TO_CAPABILITY["ghidra"])
    assert "NOT bash" in reach_instruction(BINARY_TO_CAPABILITY["ghidra"])


def test_reach_instruction_base_capability_with_service_requires_ops_start() -> None:
    # Sliver ships in the base image but is inert until its c2-sliver
    # workload runs — the hint must not claim it is directly runnable.
    sliver = BINARY_TO_CAPABILITY["sliver"]
    assert sliver.delivery == "base"
    assert sliver.requires_service == "c2-sliver"
    text = reach_instruction(sliver)
    assert "c2-sliver" in text
    assert "ops_start" in text
    assert "run it directly" not in text


def test_reach_instruction_pip_uses_break_system_packages() -> None:
    # Kali's Python is externally managed; plain pip3 install is rejected.
    vol = BINARY_TO_CAPABILITY["vol"]
    assert vol.delivery == "pip"
    text = reach_instruction(vol)
    assert "--break-system-packages" in text
    assert "volatility3" in text


def test_reach_instruction_covers_every_registry_delivery() -> None:
    # No capability should fall through to the raw delivery string.
    for cap in CAPABILITY_REGISTRY:
        text = reach_instruction(cap)
        assert text and text != cap.delivery
