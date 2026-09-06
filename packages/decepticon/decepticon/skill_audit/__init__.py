"""Skill corpus audit + canonical schema enforcement.

Provides the validator CLI used in Phase 0 cleanup. The same modules
become part of ``decepticon.skillogy.builder`` when Phase 1a lands; they
live here in their own subpackage so the validator can ship and the
corpus can be cleaned before the graph compiler exists.
"""

from decepticon.skill_audit.assessment_contract import (
    AssessmentContractError,
    decode_assessment_contract,
    normalize_assessment_contract,
)
from decepticon.skill_audit.canonical import (
    SUBDOMAIN_LIST_PATH,
    load_canonical_subdomains,
)

__all__ = [
    "AssessmentContractError",
    "decode_assessment_contract",
    "normalize_assessment_contract",
    "SUBDOMAIN_LIST_PATH",
    "load_canonical_subdomains",
]
