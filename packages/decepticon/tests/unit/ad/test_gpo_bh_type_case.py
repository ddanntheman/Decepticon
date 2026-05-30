from __future__ import annotations

from decepticon.tools.ad.bloodhound import merge_bloodhound_json
from decepticon.tools.ad.gpo import analyze_gpo_abuse
from decepticon_core.types.kg import KnowledgeGraph

_GPO_BH_PAYLOAD = {
    "meta": {"type": "gpos"},
    "data": [
        {
            "ObjectIdentifier": "GPO-1",
            "Properties": {"name": "DefaultDomainPolicy@corp.local"},
            "Aces": [{"RightName": "GenericAll", "PrincipalSID": "S-1-5-21-1-1-1-1106"}],
        }
    ],
}

_ATTACKER_PAYLOAD = {
    "meta": {"type": "users"},
    "data": [
        {
            "ObjectIdentifier": "S-1-5-21-1-1-1-1106",
            "Properties": {"name": "lowpriv@corp.local"},
            "Aces": [],
        }
    ],
}


def _graph_with_gpo_and_attacker() -> KnowledgeGraph:
    g = KnowledgeGraph()
    merge_bloodhound_json(_GPO_BH_PAYLOAD, g)
    merge_bloodhound_json(_ATTACKER_PAYLOAD, g)
    return g


def test_gpo_imported_with_canonical_bh_type() -> None:
    g = _graph_with_gpo_and_attacker()
    gpo_nodes = [n for n in g.nodes.values() if n.props.get("bh_type", "").upper() == "GPO"]
    assert len(gpo_nodes) == 1, "expected exactly one GPO node after ingest"
    assert gpo_nodes[0].props["bh_type"] == "GPO"


def test_analyze_gpo_abuse_finds_acl_abuse_via_bloodhound_ingest() -> None:
    g = _graph_with_gpo_and_attacker()
    findings = analyze_gpo_abuse(g)
    assert len(findings) >= 1, "analyze_gpo_abuse must find GenericAll on GPO node"
    assert findings[0].acl_abuse == "GenericAll"
    assert findings[0].gpo_name == "DefaultDomainPolicy@corp.local"


def test_gpo_type_comparison_case_insensitive_in_analyze() -> None:
    from decepticon_core.types.kg import Node, NodeKind

    g = KnowledgeGraph()
    gpo_node = Node.make(NodeKind.GROUP, "TestGPO", bh_type="Gpo")
    attacker = Node.make(NodeKind.USER, "attacker", bh_type="User")
    from decepticon_core.types.kg import Edge, EdgeKind

    ace_edge = Edge.make(attacker.id, gpo_node.id, EdgeKind.ENABLES, bh_right="GenericAll")
    g.upsert_node(gpo_node)
    g.upsert_node(attacker)
    g.upsert_edge(ace_edge)

    findings = analyze_gpo_abuse(g)
    assert len(findings) >= 1, "case-insensitive comparison must match bh_type='Gpo'"
