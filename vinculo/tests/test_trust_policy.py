from __future__ import annotations

from vinculo_core.types import NodeId, NodeKind
from vinculo_trust_graph import Edge, EdgeType, InMemoryTrustGraph, TrustPolicy


def _graph() -> InMemoryTrustGraph:
    g = InMemoryTrustGraph(policy=TrustPolicy(max_path_edges=2))
    g.register_node(NodeId("alice"), NodeKind.INDIVIDUAL)
    g.register_node(NodeId("bob"), NodeKind.INDIVIDUAL)
    g.register_node(NodeId("carol"), NodeKind.INDIVIDUAL)
    g.register_node(NodeId("dave"), NodeKind.INDIVIDUAL)
    g.register_node(NodeId("ifs"), NodeKind.ENTITY)
    return g


def _mutual(g: InMemoryTrustGraph, x: str, y: str) -> None:
    g.add_edge(Edge(NodeId(x), NodeId(y), EdgeType.DIRECT_CONTACT))
    g.add_edge(Edge(NodeId(y), NodeId(x), EdgeType.DIRECT_CONTACT))


def test_deny_without_relation() -> None:
    g = _graph()
    d = g.can_open_channel(NodeId("alice"), NodeId("bob"))
    assert d.allowed is False
    assert d.reason == "NO_VALID_PATH"


def test_direct_first_degree() -> None:
    g = _graph()
    _mutual(g, "alice", "bob")
    d = g.can_open_channel(NodeId("alice"), NodeId("bob"))
    assert d.allowed is True
    assert d.reason == "DIRECT_1ST_DEGREE"


def test_individual_invite_two_edges_friend_of_friend() -> None:
    """Convite indivíduo–indivíduo: Alice–Bob–Carol = 2 arestas ⇒ permitido."""
    g = _graph()
    _mutual(g, "alice", "bob")
    _mutual(g, "bob", "carol")
    d = g.can_open_channel(NodeId("alice"), NodeId("carol"))
    assert d.allowed is True
    assert d.reason == "INDIVIDUAL_INVITE_WITHIN_MAX_EDGES"
    assert d.path == ("alice", "bob", "carol")


def test_individual_invite_three_edges_denied() -> None:
    """Alice–Bob–Carol–Dave = 3 arestas ⇒ acima do máx. para indivíduo–indivíduo."""
    g = _graph()
    _mutual(g, "alice", "bob")
    _mutual(g, "bob", "carol")
    _mutual(g, "carol", "dave")
    d = g.can_open_channel(NodeId("alice"), NodeId("dave"))
    assert d.allowed is False
    assert d.reason == "NO_VALID_PATH"


def test_entity_bridge_via_membership_no_edge_cap() -> None:
    """Ponte por entidade não aplica o limite de arestas indivíduo–indivíduo."""
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


def test_entity_contacts_individual_no_edge_cap() -> None:
    g = _graph()
    g.add_edge(Edge(NodeId("alice"), NodeId("ifs"), EdgeType.RECOGNIZES))
    d = g.can_open_channel(NodeId("alice"), NodeId("ifs"))
    assert d.allowed is True
    assert d.reason == "ENTITY_TO_INDIVIDUAL"


def test_entity_still_reaches_distant_member_without_individual_path() -> None:
    """
    Entidade isenta do limite: Alice e Dave sem caminho ≤2 de contato_direto,
    mas ambos membros da entidade ⇒ canal via ponte.
    """
    g = _graph()
    _mutual(g, "alice", "bob")
    _mutual(g, "bob", "carol")
    _mutual(g, "carol", "dave")
    g.add_edge(Edge(NodeId("alice"), NodeId("ifs"), EdgeType.MEMBER_OF))
    g.add_edge(Edge(NodeId("dave"), NodeId("ifs"), EdgeType.MEMBER_OF))
    d = g.can_open_channel(NodeId("alice"), NodeId("dave"))
    assert d.allowed is True
    assert d.reason == "ENTITY_BRIDGE"
    assert d.entity == "ifs"
