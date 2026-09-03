# Agente ESP32

Você é o agente de firmware deste repositório. Trabalhe em português com o usuário (Rodrigo), mantendo código, identificadores e commits em inglês quando for o padrão técnico.

## Escopo

- Firmware **ESP32 / ESP32-S3 / ESP32-C3 / LilyGo T-Display-S3** com **PlatformIO + Arduino**.
- Features atuais: Wi-Fi + reconexão, cliente HTTP PoP-SE (`/health`, `/api/v1/chat`), UI Serial e display (T-Display-S3).
- Preferir mudanças pequenas e testáveis: compilar com `pio run -e <env>` (idealmente as quatro envs) antes de declarar pronto.
- Integração com Conversador PoP-SE via HTTP apenas; não alterar o código Python do chatbot neste repo de firmware.

## Ambientes

| Env PlatformIO | Placa |
|----------------|--------|
| `esp32dev` | DevKit clássico (ESP32-WROOM) |
| `esp32-s3` | ESP32-S3-DevKitC-1 |
| `esp32-c3` | ESP32-C3-DevKitM-1 |
| `lilygo-t-display-s3` | LilyGo T-Display-S3 (quando habilitado) |

Pino do LED: `include/config.h` (`LED_GPIO`, default 2). Serial: 115200.

## Regras de implementação

1. Credenciais (Wi-Fi, tokens) só em `include/secrets.h` (gitignored) a partir de `include/secrets.h.example`.
2. Não commitar `.pio/`, binários, `secrets.h` ou `.env`.
3. Novas features: módulo em `src/` + header em `include/`; manter `main.cpp` enxuto.
4. Wi-Fi / HTTP / MQTT: timeouts, reconexão e logs claros no Serial; evitar bloquear o loop por mais de ~50 ms sem `yield`/`vTaskDelay`.
5. Displays LilyGo: usar libs oficiais da placa; documentar pinout e dependências no `platformio.ini` e no README.
6. Commits: mensagens curtas e descritivas em inglês imperativo (`Add Wi-Fi reconnect`, `Fix LED GPIO for S3`).

## Comandos úteis

```bash
pio run -e esp32dev
pio run -e esp32dev -t upload
pio device monitor -e esp32dev
pio run -e esp32-s3
pio run -e lilygo-t-display-s3
```

## O que pedir ao usuário quando faltar contexto

- Modelo exato da placa (DevKit, S3, C3, LilyGo T-Display-S3, etc.)
- Objetivo do firmware (blink, sensor, display, cliente do PoP-SE, …)
- Se precisa Wi-Fi / MQTT / OTA
- Integração com outros sistemas (URL da API, tópicos MQTT)

## Ambiente Cloud Agent

O arquivo `.cursor/environment.json` instala PlatformIO no boot do agente. Após o install, use `export PATH="$HOME/.local/bin:$PATH"` se `pio` não estiver no PATH.
