from __future__ import annotations

from vinculo_core.types import NodeId, NodeKind
from vinculo_trust_graph import Edge, EdgeType, InMemoryTrustGraph, TrustPolicy


def _graph() -> InMemoryTrustGraph:
    g = InMemoryTrustGraph(policy=TrustPolicy(max_path_edges=2))
    g.register_node(NodeId("alice"), NodeKind.INDIVIDUAL)
    g.register_node(NodeId("bob"), NodeKind.INDIVIDUAL)
    g.register_node(NodeId("carol"), NodeKind.INDIVIDUAL)
    g.register_node(NodeId("ifs"), NodeKind.ENTITY)
    return g


def test_deny_without_relation() -> None:
    g = _graph()
    d = g.can_open_channel(NodeId("alice"), NodeId("bob"))
    assert d.allowed is False
    assert d.reason == "NO_VALID_PATH"


def test_direct_first_degree() -> None:
    g = _graph()
    g.add_edge(
        Edge(NodeId("alice"), NodeId("bob"), EdgeType.DIRECT_CONTACT)
    )
    g.add_edge(
        Edge(NodeId("bob"), NodeId("alice"), EdgeType.DIRECT_CONTACT)
    )
    d = g.can_open_channel(NodeId("alice"), NodeId("bob"))
    assert d.allowed is True
    assert d.reason == "DIRECT_1ST_DEGREE"


def test_entity_bridge_two_hops_via_membership() -> None:
    g = _graph()
    g.add_edge(Edge(NodeId("alice"), NodeId("ifs"), EdgeType.MEMBER_OF))
    g.add_edge(Edge(NodeId("bob"), NodeId("ifs"), EdgeType.MEMBER_OF))
    d = g.can_open_channel(NodeId("alice"), NodeId("bob"))
    assert d.allowed is True
    assert d.reason == "ENTITY_BRIDGE"
    assert d.entity == "ifs"
    assert d.path == ("alice", "ifs", "bob")


def test_entity_bridge_via_authorizes_pair() -> None:
    g = _graph()
    g.add_edge(Edge(NodeId("alice"), NodeId("ifs"), EdgeType.RECOGNIZES))
    g.add_edge(Edge(NodeId("carol"), NodeId("ifs"), EdgeType.RECOGNIZES))
    g.add_edge(
        Edge(
            NodeId("ifs"),
            NodeId("alice"),
            EdgeType.AUTHORIZES_PAIR,
            pair_with=NodeId("carol"),
        )
    )
    d = g.can_open_channel(NodeId("alice"), NodeId("carol"))
    assert d.allowed is True
    assert d.reason == "ENTITY_BRIDGE"


def test_no_three_hop_friend_of_friend() -> None:
    """Alice conhece Bob; Bob conhece Carol — sem entidade compartilhada ⇒ negado."""
    g = _graph()
    g.add_edge(Edge(NodeId("alice"), NodeId("bob"), EdgeType.DIRECT_CONTACT))
    g.add_edge(Edge(NodeId("bob"), NodeId("alice"), EdgeType.DIRECT_CONTACT))
    g.add_edge(Edge(NodeId("bob"), NodeId("carol"), EdgeType.DIRECT_CONTACT))
    g.add_edge(Edge(NodeId("carol"), NodeId("bob"), EdgeType.DIRECT_CONTACT))
    d = g.can_open_channel(NodeId("alice"), NodeId("carol"))
    assert d.allowed is False


def test_entity_contacts_individual() -> None:
    g = _graph()
    g.add_edge(Edge(NodeId("alice"), NodeId("ifs"), EdgeType.RECOGNIZES))
    d = g.can_open_channel(NodeId("alice"), NodeId("ifs"))
    assert d.allowed is True
    assert d.reason == "ENTITY_TO_INDIVIDUAL"
