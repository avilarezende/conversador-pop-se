"""Rate limiting do engine (slowapi): protege /chat e /rag/ingest de abuso."""

import os

from slowapi import Limiter
from slowapi.util import get_remote_address

# Desativável em testes/dev com ENGINE_RATE_LIMIT_ENABLED=0.
_enabled = os.getenv("ENGINE_RATE_LIMIT_ENABLED", "1") != "0"

limiter = Limiter(key_func=get_remote_address, enabled=_enabled, storage_uri="memory://")

CHAT_LIMIT = "60/minute"      # mensagens de chat por origem
INGEST_LIMIT = "10/minute"    # ingestão de documentos (operações pesadas)