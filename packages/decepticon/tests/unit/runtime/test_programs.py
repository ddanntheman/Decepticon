"""Telemetry allowlist invariants for the expanded tool arsenal.

The privacy-preserving program capture (:mod:`decepticon.runtime.programs`)
only measures "was the arsenal used?" if every tool the sandbox actually
ships is on the allowlist. These tests lock that — and the internal
consistency of the allowlist subsets — so a future tool addition that
forgets the telemetry side is caught in CI, not months later in a blind
retrospective.
"""

from __future__ import annotations

import pytest

from decepticon.runtime.programs import (
    GENERIC_PROGRAMS,
    KNOWN_PROGRAMS,
    SECURITY_PROGRAMS,
    WEB_SCANNER_PROGRAMS,
    extract_programs,
)
from decepticon_core.capabilities import security_binaries

# The headless tranche added to the base sandbox image — each must be
# capturable or its usage is invisible to under-use analysis.
_TRANCHE = (
    "ffuf",
    "feroxbuster",
    "nuclei",
    "httpx-toolkit",
    "whatweb",
    "wafw00f",
    "commix",
    "dalfox",
    "testssl",
    "sslscan",
    "sslyze",
    "gitleaks",
    "trufflehog",
    "tcpdump",
    "tshark",
    "enum4linux",
    "netexec",
)


@pytest.mark.parametrize("prog", _TRANCHE)
def test_tranche_tools_are_captured(prog: str) -> None:
    assert prog in KNOWN_PROGRAMS, f"{prog} not in telemetry allowlist"


@pytest.mark.parametrize("prog", _TRANCHE)
def test_extract_programs_recognizes_tranche(prog: str) -> None:
    # A realistic invocation with a path prefix and arguments must still
    # resolve to the bare basename.
    assert extract_programs(f"/usr/bin/{prog} -u https://target.example") == [prog]


def test_web_scanner_subset_of_security() -> None:
    assert WEB_SCANNER_PROGRAMS <= SECURITY_PROGRAMS


def test_security_and_generic_disjoint_except_dual_use() -> None:
    """Programs are classified security XOR generic; the only overlaps are
    dual-use network utilities intentionally tracked as generic."""
    overlap = SECURITY_PROGRAMS & GENERIC_PROGRAMS
    assert overlap <= {"nc", "ncat", "socat"}


def test_every_shipped_security_binary_is_known() -> None:
    """Registry-shipped security binaries must all be capturable."""
    uncapturable = {b for b in security_binaries() if b not in KNOWN_PROGRAMS}
    assert not uncapturable, sorted(uncapturable)


def test_extract_programs_caps_and_dedupes() -> None:
    cmd = " && ".join(["nmap -sV target"] * 20)
    progs = extract_programs(cmd)
    assert progs == ["nmap"]  # deduped
