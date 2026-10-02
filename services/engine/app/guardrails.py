"""Guardrails: mantêm o Calisto restrito ao escopo do PoP-SE/RNP.

Duas camadas:
1. Determinística (esta): regras configuráveis avaliadas antes de chamar a IA.
   - ``blocked_keywords``: bloqueia se a mensagem contém palavras vetadas.
   - ``scope``: bloqueia se a mensagem não contém nenhuma palavra do escopo.
2. Instrução no prompt do sistema (``SCOPE_GUIDANCE``): defesa em profundidade.
"""

from __future__ import annotations

from dataclasses import dataclass

# Palavras que caracterizam o escopo do PoP-SE/RNP (conectividade e conversa).
_SCOPE_KEYWORDS = [
    # Conectividade / operação
    "conectividade", "conexao", "conexão", "internet", "rede", "link", "enlace",
    "banda", "trafego", "tráfego", "latencia", "latência", "manutencao", "manutenção",
    "chamado", "incidente", "problema", "alerta", "monitor", "zabbix", "cacti",
    "grafana", "fibra", "roteador", "switch", "backbone", "operadora", "provedor",
    "servico", "serviço", "status", "funcionando", "caiu", "lento", "instabilidade",
    "e-mail", "email", "disponibilidade", "queda",
    # Institucional
    "rnp", "pop", "pop-se", "sergipe", "instituicao", "instituição", "instituto",
    "universidade", "campus", "ifs", "ufs", "ebserh", "hu",
    # Conversa / identidade / cortesia
    "bom dia", "boa tarde", "boa noite", "ola", "olá", "oi ", "sou ", "meu nome",
    "obrigado", "obrigada", "ajuda", "ajudar", "pode", "poderia", "gostaria",
    "senhor", "senhora", "tudo bem", "quem e voce", "quem é você", "o que voce faz",
    "o que você faz", "calisto",
]

DEFAULT_GUARDRAILS: list[dict] = [
    {
        "id": "scope-popse",
        "name": "Escopo PoP-SE/RNP",
        "type": "scope",
        "enabled": True,
        "keywords": list(_SCOPE_KEYWORDS),
        "message": (
            "Desculpe, sou o Calisto, assistente do PoP-SE/RNP, e só consigo ajudar "
            "com temas de conectividade, links, manutenções, monitoração e serviços "
            "da RNP em Sergipe. Poderia reformular a sua pergunta dentro desse escopo? "
            "Se precisar de outro assunto, contate o PoP-SE em info@pop-se.rnp.br."
        ),
    },
    {
        "id": "off-topic-examples",
        "name": "Assuntos fora de contexto",
        "type": "blocked_keywords",
        "enabled": True,
        "keywords": [
            "receita", "futebol", "namoro", "piada", "horoscopo", "horóscopo",
            "bitcoin", "criptomoeda", "aposta", "loteria",
        ],
        "message": (
            "Esse tema foge do meu escopo. Sou o Calisto e ajudo apenas com assuntos "
            "de conectividade e serviços do PoP-SE/RNP. Posso ajudar com algo "
            "relacionado à sua instituição?"
        ),
    },
]

SCOPE_GUIDANCE = (
    "\n\nIMPORTANTE — Escopo: você só deve responder sobre temas do PoP-SE/RNP "
    "(conectividade, links, manutenções, monitoração, chamados e serviços às "
    "instituições clientes em Sergipe). Se a pergunta fugir desse escopo, recuse "
    "educadamente e ofereça ajuda dentro do contexto do PoP-SE."
)


@dataclass
class GuardrailResult:
    allowed: bool
    message: str | None = None
    guardrail_id: str | None = None


def evaluate_message(message: str, guardrails: list[dict] | None = None) -> GuardrailResult:
    """Avalia a mensagem do usuário contra as regras ativas."""
    if guardrails is None:
        from app.settings_store import list_guardrails

        guardrails = list_guardrails()

    text = (message or "").lower()

    # 1) Palavras vetadas (mais específico).
    for g in guardrails:
        if not g.get("enabled", True) or g.get("type") != "blocked_keywords":
            continue
        for kw in g.get("keywords", []):
            if kw and kw in text:
                return GuardrailResult(False, g.get("message"), g.get("id"))

    # 2) Escopo: bloqueia se não houver nenhuma palavra do escopo.
    for g in guardrails:
        if not g.get("enabled", True) or g.get("type") != "scope":
            continue
        keywords = g.get("keywords", [])
        if keywords and not any(kw in text for kw in keywords):
            return GuardrailResult(False, g.get("message"), g.get("id"))

    return GuardrailResult(True)
