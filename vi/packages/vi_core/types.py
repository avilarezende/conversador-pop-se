from __future__ import annotations

from enum import StrEnum
from typing import NewType

NodeId = NewType("NodeId", str)
ConversationId = NewType("ConversationId", str)
AnchorId = NewType("AnchorId", str)


class NodeKind(StrEnum):
    INDIVIDUAL = "individual"
    ENTITY = "entity"
