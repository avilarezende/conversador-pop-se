from __future__ import annotations

import secrets
from dataclasses import dataclass

from vinculo_core.errors import PolicyDenied
from vinculo_core.types import ConversationId, NodeId


@dataclass
class _Session:
    session_id: str
    conversation_id: ConversationId
    initiator: NodeId
    peer: NodeId
    active: bool = True


class RealtimeSessionService:
    """Stub de sessões A/V — habilitado só se o módulo estiver ativo."""

    def __init__(self, *, enabled: bool = False) -> None:
        self.enabled = enabled
        self._sessions: dict[str, _Session] = {}

    def start_session(
        self, conversation_id: ConversationId, initiator: NodeId, peer: NodeId
    ) -> str:
        if not self.enabled:
            raise PolicyDenied("REALTIME_AV_DISABLED")
        session_id = secrets.token_hex(8)
        self._sessions[session_id] = _Session(
            session_id=session_id,
            conversation_id=conversation_id,
            initiator=initiator,
            peer=peer,
        )
        return session_id

    def end_session(self, session_id: str) -> None:
        session = self._sessions.get(session_id)
        if session:
            session.active = False
