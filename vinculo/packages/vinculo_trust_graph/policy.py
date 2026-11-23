from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime

from vinculo_core.types import NodeId
from vinculo_trust_graph.models import Anchor, Decision, Edge, EdgeType


@dataclass
class TrustPolicy:
    """
    Regras R1–R4.

    O limite ``max_path_edges`` vale **somente** para convites/canais
    indivíduo↔indivíduo via arestas ``contato_direto``. Entidades reconhecidas
    não estão sujeitas a esse limite (contato direto ou ponte/autorização).
    """

    max_path_edges: int = 2  # só indivíduo–indivíduo
    require_anchor_for_entity_bridge: bool = False

    def decide(
        self,
        a: NodeId,
        b: NodeId,
        *,
        at: datetime,
        edges: list[Edge],
        anchors: dict[str, Anchor],
        entity_ids: set[NodeId],
    ) -> Decision:
        if a == b:
            return Decision(False, "SAME_NODE")

        # R2 — entidade ↔ indivíduo: sem limite de arestas
        if b in entity_ids and self._recognizes(a, b, edges):
            return Decision(True, "ENTITY_TO_INDIVIDUAL", entity=b, path=(a, b))
        if a in entity_ids and self._recognizes(b, a, edges):
            return Decision(True, "ENTITY_TO_INDIVIDUAL", entity=a, path=(b, a))

        both_individuals = a not in entity_ids and b not in entity_ids

        if both_individuals:
            if self._mutual_direct(a, b, edges):
                return Decision(True, "DIRECT_1ST_DEGREE", path=(a, b))

            # Convite indivíduo–indivíduo: no máx. max_path_edges arestas
            path = self._shortest_mutual_contact_path(
                a, b, edges, entity_ids, self.max_path_edges
            )
            if path is not None:
                return Decision(
                    True,
                    "INDIVIDUAL_INVITE_WITHIN_MAX_EDGES",
                    path=tuple(path),
                )

            # R3 — ponte por entidade: sem limite de arestas na entidade
            shared = self._shared_recognized_entities(a, b, edges, entity_ids)
            for entity in shared:
                if not self._entity_permits_pair(entity, a, b, edges):
                    continue
                if self.require_anchor_for_entity_bridge:
                    if not self._bridge_anchor_valid(
                        entity, a, b, edges, anchors, at
                    ):
                        continue
                return Decision(
                    True,
                    "ENTITY_BRIDGE",
                    entity=entity,
                    path=(a, entity, b),
                )

        return Decision(False, "NO_VALID_PATH")

    def _mutual_direct(self, a: NodeId, b: NodeId, edges: list[Edge]) -> bool:
        ab = any(
            e.edge_type == EdgeType.DIRECT_CONTACT and e.src == a and e.dst == b
            for e in edges
        )
        ba = any(
            e.edge_type == EdgeType.DIRECT_CONTACT and e.src == b and e.dst == a
            for e in edges
        )
        return ab and ba

    def _shortest_mutual_contact_path(
        self,
        a: NodeId,
        b: NodeId,
        edges: list[Edge],
        entity_ids: set[NodeId],
        max_edges: int,
    ) -> list[NodeId] | None:
        """BFS só em indivíduos ligados por contato_direto mútuo."""
        adj: dict[NodeId, set[NodeId]] = defaultdict(set)
        directed: set[tuple[NodeId, NodeId]] = set()
        for e in edges:
            if e.edge_type != EdgeType.DIRECT_CONTACT:
                continue
            if e.src in entity_ids or e.dst in entity_ids:
                continue
            directed.add((e.src, e.dst))
        for src, dst in directed:
            if (dst, src) in directed:
                adj[src].add(dst)

        if a not in adj and a != b:
            return None

        queue: deque[tuple[NodeId, list[NodeId]]] = deque([(a, [a])])
        seen = {a}
        while queue:
            node, path = queue.popleft()
            edge_count = len(path) - 1
            if edge_count >= max_edges:
                continue
            for nbr in adj[node]:
                if nbr in seen:
                    continue
                next_path = path + [nbr]
                if nbr == b:
                    return next_path
                seen.add(nbr)
                queue.append((nbr, next_path))
        return None

    def _recognizes(self, person: NodeId, entity: NodeId, edges: list[Edge]) -> bool:
        return any(
            e.edge_type in (EdgeType.RECOGNIZES, EdgeType.MEMBER_OF)
            and e.src == person
            and e.dst == entity
            for e in edges
        )

    def _shared_recognized_entities(
        self,
        a: NodeId,
        b: NodeId,
        edges: list[Edge],
        entity_ids: set[NodeId],
    ) -> list[NodeId]:
        a_ents = {
            e.dst
            for e in edges
            if e.src == a
            and e.dst in entity_ids
            and e.edge_type in (EdgeType.RECOGNIZES, EdgeType.MEMBER_OF)
        }
        b_ents = {
            e.dst
            for e in edges
            if e.src == b
            and e.dst in entity_ids
            and e.edge_type in (EdgeType.RECOGNIZES, EdgeType.MEMBER_OF)
        }
        return sorted(a_ents & b_ents)

    def _entity_permits_pair(
        self, entity: NodeId, a: NodeId, b: NodeId, edges: list[Edge]
    ) -> bool:
        for e in edges:
            if e.edge_type != EdgeType.AUTHORIZES_PAIR or e.src != entity:
                continue
            pair = {e.dst, e.pair_with}
            if pair == {a, b}:
                return True
        a_member = any(
            e.edge_type == EdgeType.MEMBER_OF and e.src == a and e.dst == entity
            for e in edges
        )
        b_member = any(
            e.edge_type == EdgeType.MEMBER_OF and e.src == b and e.dst == entity
            for e in edges
        )
        return a_member and b_member

    def _bridge_anchor_valid(
        self,
        entity: NodeId,
        a: NodeId,
        b: NodeId,
        edges: list[Edge],
        anchors: dict[str, Anchor],
        at: datetime,
    ) -> bool:
        for e in edges:
            if e.edge_type != EdgeType.AUTHORIZES_PAIR or e.src != entity:
                continue
            if {e.dst, e.pair_with} != {a, b}:
                continue
            if e.anchor_id is None:
                return False
            anchor = anchors.get(str(e.anchor_id))
            if anchor and anchor.is_valid_at(at):
                return True
        return False
