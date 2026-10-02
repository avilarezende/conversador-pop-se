# ESP32-CYD — Calisto + Grok

Projeto **standalone** (sem PoP-SE): firmware para o Cheap Yellow Display com avatar **Calisto** e conversa direta com **xAI Grok**.

## Recursos

- Display ILI9341 320×240 + toque XPT2046
- Avatar animado (pisca / pensa / fala)
- Chips: Olá · Piada · Quem? · ? · OK
- Mensagens livres via Serial 115200
- Cliente HTTPS → `api.x.ai/v1/chat/completions`
- Simulador web em `simulator/`
- Agentes Cursor em `AGENTS.md` + `agents/`
- Ambiente Cloud Agent nomeado **esp32**

## Setup rápido

```bash
cp include/secrets.h.example include/secrets.h
# WIFI_SSID, WIFI_PASSWORD, GROK_API_KEY
pio run -e cyd -t upload
pio device monitor -e cyd
```

Chave Grok: https://console.x.ai

## Simulador

```bash
cd simulator && python3 -m http.server 8765
# http://localhost:8765
```

## Agentes / ambiente

| Item | Onde |
|------|------|
| Agente geral | `AGENTS.md` |
| Firmware | `agents/firmware.md` |
| UX avatar | `agents/ux-avatar.md` |
| Cloud env | `.cursor/environment.json` (`name: esp32`) |

Publique este diretório como repo próprio (`make publish`) e aponte um Cloud Agent Environment chamado **esp32** para ele — não use o environment do Conversador PoP-SE.

## Make

```bash
make build
make contract
make simulator
make publish
```
