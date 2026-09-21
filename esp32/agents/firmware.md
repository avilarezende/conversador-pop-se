# Agente — Firmware ESP32-CYD

Foque em PlatformIO, pinout do Cheap Yellow Display, Wi-Fi, TLS/HTTP e `grok_client`.

## Checklist

- Compilar com `pio run -e cyd` (e `cyd-noled` se mudar flags de LED).
- Não bloquear o `loop` por longos períodos sem `yield`.
- Timeouts HTTP generosos para Grok (`GROK_HTTP_TIMEOUT_MS`).
- Credenciais apenas em `secrets.h`.
- Documentar mudanças de pinout no `platformio.ini` e README.

## Fora de escopo

- Não criar dependências de outros repositórios ou engines.
- Não alterar o simulador web salvo se o contrato JSON/API mudar.
