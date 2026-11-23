from __future__ import annotations

from typing import Protocol

from vi_core.types import ConversationId, NodeId


class RealtimeSessionPort(Protocol):
    def start_session(
        self, conversation_id: ConversationId, initiator: NodeId, peer: NodeId
    ) -> str:
        """Retorna session_id."""
        ...

    def end_session(self, session_id: str) -> None: ...
