# Cloud Agent — ambiente esp32

1. Este projeto é **standalone** (sem PoP-SE).
2. Publique com `make publish` → `avilarezende/esp32`.
3. Crie um Cloud Agent Environment chamado **esp32** ligado só a esse repo.
4. Secret: `GROK_API_KEY`.
5. Smoke: `python3 tests/test_grok_contract.py` + `simulator/`.
