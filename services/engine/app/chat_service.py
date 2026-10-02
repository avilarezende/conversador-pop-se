"""Orquestração da conversa."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.guardrails import SCOPE_GUIDANCE, evaluate_message
from app.llm import generate_reply
from app.memory import (
    get_recent_messages,
    save_message,
    update_user_from_message,
    user_context_summary,
)
from app.models import User
from app.persona import SYSTEM_PROMPT
from app.rag import query_context


async def _format_history(messages) -> str:
    """Transforma as mensagens recentes em blocos de histórico conversacional."""
    if not messages:
        return ""
    lines = []
    for msg in messages:
        role = "Usuário" if msg.role == "user" else "Assistente"
        lines.append(f"{role}: {msg.content}")
    return "\n".join(lines)


async def handle_chat(
    session: AsyncSession,
    user: User,
    message: str,
) -> str:
    user = await update_user_from_message(session, user, message)
    await save_message(session, user, "user", message)

    # Guardrails: barra mensagens fora do escopo antes de acionar a IA.
    verdict = evaluate_message(message)
    if not verdict.allowed:
        refusal = verdict.message or (
            "Desculpe, só posso ajudar com assuntos do PoP-SE/RNP."
        )
        await save_message(session, user, "assistant", refusal)
        return refusal

    inst_sigla = user.instituicao_sigla  # None se não identificado ainda
    rag_context = query_context("operacional", message, top_k=6, instituicao=inst_sigla)
    inst_context = query_context("institucional", message, top_k=3, instituicao=inst_sigla)
    maint_context = query_context("manutencoes", message, top_k=4, instituicao=inst_sigla)
    history = await _format_history(await get_recent_messages(session, user, limit=8))

    full_context = "\n\n".join(
        filter(
            None,
            [
                f"Dados do usuário:\n{await user_context_summary(user)}",
                f"Histórico da conversa:\n{history}" if history else "",
                f"Fontes operacionais:\n{rag_context}" if rag_context else "",
                f"Contexto institucional:\n{inst_context}" if inst_context else "",
                f"Manutenções:\n{maint_context}" if maint_context else "",
            ],
        )
    )

    reply = await generate_reply(SYSTEM_PROMPT + SCOPE_GUIDANCE, message, full_context)
    await save_message(session, user, "assistant", reply)
    return reply
