#!/usr/bin/env python3
"""Contrato do cliente Grok usado pelo firmware CYD (sem hardware)."""

from __future__ import annotations

import json
import sys
import unittest


def infer_mood(reply: str) -> str:
    low = reply.lower()
    if any(w in low for w in ("desculpe", "problema", "falha", "infelizmente")):
        return "concerned"
    if any(w in low for w in ("bom dia", "tudo bem", "otimo", "ótimo", "prazer")):
        return "happy"
    return "speaking"


CHAT_RESPONSE = {
    "choices": [
        {
            "message": {
                "role": "assistant",
                "content": "Oi! Tudo bem. Sou Calisto neste display.",
            }
        }
    ]
}


class GrokContractTests(unittest.TestCase):
    def test_chat_response_shape(self) -> None:
        body = json.loads(json.dumps(CHAT_RESPONSE))
        content = body["choices"][0]["message"]["content"]
        self.assertTrue(len(content) > 0)

    def test_request_payload(self) -> None:
        req = {
            "model": "grok-2-latest",
            "messages": [
                {"role": "system", "content": "You are Calisto."},
                {"role": "user", "content": "Ola!"},
            ],
        }
        parsed = json.loads(json.dumps(req))
        self.assertEqual(parsed["model"], "grok-2-latest")
        self.assertEqual(len(parsed["messages"]), 2)

    def test_infer_mood(self) -> None:
        self.assertEqual(infer_mood("Oi! Tudo bem por aqui."), "happy")
        self.assertEqual(infer_mood("Infelizmente houve uma falha."), "concerned")
        self.assertEqual(infer_mood("Posso te explicar o display."), "speaking")


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
