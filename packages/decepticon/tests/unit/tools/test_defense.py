"""Tests for decepticon.tools.defense."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from decepticon.tools.defense import conops as conops_mod
from decepticon.tools.defense.edr import _extract_yara_metadata
from decepticon.tools.defense.elastic import (
    SigmaToElasticError,
    sigma_to_lucene,
)
from decepticon.tools.defense.sentinel import (
    SigmaToKqlError,
    sigma_to_kql,
)
from decepticon.tools.defense.splunk import (
    SigmaConversionError,
    sigma_to_spl,
)


def _basic_sigma() -> dict:
    return {
        "title": "test-rule",
        "logsource": {"product": "windows", "category": "process_creation"},
        "detection": {
            "selection": {
                "Image|endswith": "\\powershell.exe",
                "CommandLine|contains": "DownloadString",
            },
            "condition": "selection",
        },
    }


def test_sigma_to_spl_basic():
    spl = sigma_to_spl(_basic_sigma())
    assert "Image=*\\powershell.exe" in spl
    assert "CommandLine=*DownloadString*" in spl


def test_sigma_to_spl_with_or_condition():
    rule = {
        "detection": {
            "selA": {"a": "1"},
            "selB": {"b": "2"},
            "condition": "selA or selB",
        }
    }
    spl = sigma_to_spl(rule)
    assert "OR" in spl
    assert "a=" in spl and "b=" in spl


def test_sigma_to_spl_with_list_value():
    rule = {
        "detection": {
            "sel": {"Image|endswith": ["\\cmd.exe", "\\powershell.exe"]},
            "condition": "sel",
        }
    }
    spl = sigma_to_spl(rule)
    assert "Image=*\\cmd.exe" in spl
    assert "Image=*\\powershell.exe" in spl


def test_sigma_to_spl_unknown_modifier_raises():
    rule = {
        "detection": {
            "sel": {"field|exotic_modifier": "x"},
            "condition": "sel",
        }
    }
    with pytest.raises(SigmaConversionError):
        sigma_to_spl(rule)


def test_sigma_to_spl_unknown_selection_raises():
    rule = {
        "detection": {
            "selA": {"a": "1"},
            "condition": "missing_selection",
        }
    }
    with pytest.raises(SigmaConversionError):
        sigma_to_spl(rule)


def test_sigma_to_kql_picks_security_event_for_windows():
    kql = sigma_to_kql(_basic_sigma())
    assert kql.startswith("SecurityEvent")
    assert "where" in kql
    assert 'endswith "\\\\powershell.exe"' in kql or "endswith" in kql


def test_sigma_to_kql_unknown_modifier_raises():
    rule = {
        "logsource": {"product": "windows", "category": "process_creation"},
        "detection": {
            "sel": {"field|nope": "x"},
            "condition": "sel",
        },
    }
    with pytest.raises(SigmaToKqlError):
        sigma_to_kql(rule)


def test_sigma_to_lucene_basic():
    lucene = sigma_to_lucene(_basic_sigma())
    assert "Image: *\\powershell.exe" in lucene
    assert "CommandLine: *DownloadString*" in lucene


def test_sigma_to_lucene_unknown_token_raises():
    rule = {
        "detection": {
            "sel": {"a": "1"},
            "condition": "sel xor what",
        }
    }
    with pytest.raises(SigmaToElasticError):
        sigma_to_lucene(rule)


def test_extract_yara_metadata_pulls_meta_kvs():
    yara = """
    rule foo {
      meta:
        author = "decepticon"
        indicator_type = "sha256"
        indicator_value = "deadbeef"
      strings:
        $a = "x"
      condition:
        $a
    }
    """
    meta = _extract_yara_metadata(yara)
    assert meta["author"] == "decepticon"
    assert meta["indicator_type"] == "sha256"
    assert meta["indicator_value"] == "deadbeef"


def test_extract_yara_metadata_empty_when_no_meta_block():
    yara = "rule bar { strings: $a = \"x\" condition: $a }"
    assert _extract_yara_metadata(yara) == {}


def test_resolve_siem_target_missing_conops_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    monkeypatch.setenv("DECEPTICON_ENGAGEMENT_WORKSPACE", str(tmp_path))
    with pytest.raises(conops_mod.ConOpsLookupError):
        conops_mod.resolve_siem_target("splunk")


def test_resolve_siem_target_missing_target_raises(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    (tmp_path / "conops.json").write_text(json.dumps({"blue_team": {}}))
    monkeypatch.setenv("DECEPTICON_ENGAGEMENT_WORKSPACE", str(tmp_path))
    with pytest.raises(conops_mod.ConOpsLookupError):
        conops_mod.resolve_siem_target("splunk")


def test_resolve_siem_target_success(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
):
    (tmp_path / "conops.json").write_text(
        json.dumps(
            {
                "blue_team": {
                    "splunk": {"url": "https://splunk.example", "auth": "hec_token:HEC_TOKEN"}
                }
            }
        )
    )
    monkeypatch.setenv("DECEPTICON_ENGAGEMENT_WORKSPACE", str(tmp_path))
    target = conops_mod.resolve_siem_target("splunk")
    assert target["url"] == "https://splunk.example"


def test_resolve_auth_value_missing_env_raises(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.delenv("NOT_SET_AT_ALL", raising=False)
    with pytest.raises(conops_mod.ConOpsLookupError):
        conops_mod.resolve_auth_value("hec_token:NOT_SET_AT_ALL")


def test_resolve_auth_value_success(monkeypatch: pytest.MonkeyPatch):
    monkeypatch.setenv("SOME_TOKEN", "supersecret")
    assert conops_mod.resolve_auth_value("hec_token:SOME_TOKEN") == "supersecret"
