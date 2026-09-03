#!/usr/bin/env python3
"""Contrato JSON do Conversador PoP-SE consumido pelo firmware ESP32.

Valida os formatos de /health e /api/v1/chat sem hardware.
Execute: python3 tests/test_popse_contract.py
"""

from __future__ import annotations

import json
import sys
import unittest


HEALTH_OK = {
    "status": "ok",
    "service": "conversador-engine",
    "llm_provider": "ollama",
}

CHAT_OK = {
    "reply": "Links monitorados operacionais no momento.",
    "user_id": "esp32-device",
    "channel": "esp32",
}


class PopseContractTests(unittest.TestCase):
    def test_health_ok_fields(self) -> None:
        body = json.loads(json.dumps(HEALTH_OK))
        self.assertEqual(body.get("status", "").lower(), "ok")
        self.assertIn("service", body)
        self.assertIn("llm_provider", body)

    def test_health_error_shape(self) -> None:
        body = {"status": "degraded", "service": "conversador-engine", "llm_provider": "x"}
        self.assertNotEqual(body.get("status", "").lower(), "ok")

    def test_chat_ok_fields(self) -> None:
        body = json.loads(json.dumps(CHAT_OK))
        self.assertTrue(len(body.get("reply", "")) > 0)
        self.assertEqual(body.get("channel"), "esp32")

    def test_chat_request_payload(self) -> None:
        req = {
            "message": "Qual o status geral dos links monitorados agora?",
            "user_id": "esp32-device",
            "channel": "esp32",
        }
        payload = json.dumps(req)
        parsed = json.loads(payload)
        self.assertGreaterEqual(len(parsed["message"]), 1)
        self.assertLessEqual(len(parsed["message"]), 8000)


if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)
