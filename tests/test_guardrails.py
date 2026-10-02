"""Testes dos guardrails de escopo do Calisto."""

from app.guardrails import DEFAULT_GUARDRAILS, evaluate_message


def test_in_scope_message_allowed():
    result = evaluate_message(
        "Bom dia, o link principal do IFS está lento hoje?", DEFAULT_GUARDRAILS
    )
    assert result.allowed is True


def test_greeting_allowed():
    result = evaluate_message("Bom dia!", DEFAULT_GUARDRAILS)
    assert result.allowed is True


def test_out_of_scope_blocked():
    result = evaluate_message("Quanto é dois mais dois?", DEFAULT_GUARDRAILS)
    assert result.allowed is False
    assert result.message


def test_blocked_keyword():
    result = evaluate_message("Me dá uma receita de bolo de chocolate?", DEFAULT_GUARDRAILS)
    assert result.allowed is False
    assert result.guardrail_id == "off-topic-examples"


def test_disabled_guardrail_is_ignored():
    guardrails = [
        {
            "id": "scope-popse",
            "name": "Escopo",
            "type": "scope",
            "enabled": False,
            "keywords": ["rnp"],
            "message": "fora de escopo",
        }
    ]
    result = evaluate_message("qualquer coisa aleatória", guardrails)
    assert result.allowed is True
