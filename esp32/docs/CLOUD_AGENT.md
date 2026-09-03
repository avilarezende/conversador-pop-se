# Cloud Agent — repositório ESP32

Instruções para publicar o firmware e abrir um **Cloud Agent dedicado** em `avilarezende/esp32`.

## 1. Publicar o repositório GitHub

Na máquina local (conta `avilarezende` com permissão de criar repos):

```bash
# a partir deste monorepo / PR
cd esp32
./scripts/publish-github.sh
```

URL esperada: https://github.com/avilarezende/esp32

> O token do Cloud Agent atual (ligado a `conversador-pop-se`) **não** tem `createRepository` (HTTP 403). Por isso a publicação precisa ser feita na sua conta.

## 2. Criar o Cloud Agent

1. Abra https://cursor.com/agents
2. **New Agent**
3. Selecione o repositório **`avilarezende/esp32`** (não o Conversador PoP-SE)
4. Environment: use `.cursor/environment.json` deste projeto (instala PlatformIO)
5. O agente lê `AGENTS.md` e `.cursor/rules/esp32-firmware.mdc`

### Prompts iniciais úteis

- `pio run -e lilygo-t-display-s3` e corrija qualquer falha de build
- Adicione MQTT para publicar o status do `/health`
- Mostre no display a resposta do chat truncada em 3 linhas

## 3. Configurar secrets no device

```bash
cp include/secrets.h.example include/secrets.h
# WIFI_* e POPSE_ENGINE_URL
```

## 4. Validação sem hardware

```bash
cd esp32
python3 tests/test_popse_contract.py
pio run -e esp32dev -e esp32-s3 -e esp32-c3 -e lilygo-t-display-s3
```
