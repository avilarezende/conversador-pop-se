# ESP32 — companion PoP-SE

Firmware **PlatformIO + Arduino** para ESP32 (DevKit, S3, C3 e LilyGo T-Display-S3).

Funções atuais:
- Wi-Fi com reconexão
- Polling de `GET /health` do Conversador PoP-SE
- Consulta `POST /api/v1/chat` (botão BOOT nas placas com `BOARD_HAS_BOOT_BTN`)
- UI Serial; no T-Display-S3, status no display ST7789

Inclui **AGENTS.md** e `.cursor/` para o Cloud Agent / agente Cursor.

## Requisitos

- [PlatformIO Core](https://docs.platformio.org/en/latest/core/installation/index.html) ou extensão PlatformIO
- Cabo USB e drivers (CP210x, CH340 ou USB-JTAG nativo no S3/C3)
- Credenciais em `include/secrets.h` (copie de `secrets.h.example`)

## Configuração

```bash
cp include/secrets.h.example include/secrets.h
# edite WIFI_SSID, WIFI_PASSWORD, POPSE_ENGINE_URL
```

| Macro | Função |
|-------|--------|
| `WIFI_SSID` / `WIFI_PASSWORD` | Rede Wi-Fi |
| `POPSE_ENGINE_URL` | Base do engine (ex. `http://192.168.1.10:8000`) |
| `POPSE_USER_ID` | ID do dispositivo no chat |
| `POPSE_POLL_INTERVAL_MS` | Intervalo do `/health` (default 30s) |

## Compilar e gravar

```bash
pio run -e esp32dev -t upload && pio device monitor -e esp32dev
pio run -e esp32-s3 -t upload
pio run -e esp32-c3 -t upload
pio run -e lilygo-t-display-s3 -t upload
```

No T-Display-S3: pressione o botão **BOOT** (GPIO 0) para perguntar ao engine sobre o status dos links.

## Estrutura

```
esp32/
├── AGENTS.md
├── platformio.ini
├── include/config.h
├── include/wifi_manager.h
├── include/popse_client.h
├── include/status_ui.h
├── include/secrets.h.example
├── src/main.cpp
├── src/wifi_manager.cpp
├── src/popse_client.cpp
├── src/status_ui.cpp
└── .cursor/   environment + rules do agente
```

## Agente Cursor

### Local / IDE

Abra a pasta `esp32/` (ou o repo `avilarezende/esp32`). `AGENTS.md` e `.cursor/rules/` orientam o agente.

### Cloud Agent

1. Publique o repositório no GitHub (seção abaixo).
2. Em [Cloud Agents](https://cursor.com/agents) → **New Agent**.
3. Selecione `avilarezende/esp32` (não o Conversador PoP-SE).
4. Environment: `.cursor/environment.json` instala PlatformIO.

## Hospedagem temporária

Enquanto `avilarezende/esp32` não existir no GitHub, este projeto vive na pasta `esp32/` do repositório [conversador-pop-se](https://github.com/avilarezende/conversador-pop-se). O Cloud Agent dedicado deve apontar para o repositório ESP32 separado.

## Publicar como repositório próprio

```bash
cd esp32
git init -b main
git add -A
git commit -m "Initial commit: ESP32 PoP-SE companion firmware."
gh repo create avilarezende/esp32 --public --source=. --remote=origin --push
```
