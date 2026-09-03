# ESP32

Repositório de firmware para placas **ESP32** (DevKit, S3, C3 e LilyGo T-Display-S3), gerenciado com [PlatformIO](https://platformio.org/).

Inclui **AGENTS.md** e regras em `.cursor/` para o Cloud Agent / agente de código do Cursor.

## Requisitos

- [PlatformIO Core](https://docs.platformio.org/en/latest/core/installation/index.html) ou a extensão PlatformIO no VS Code / Cursor
- Cabo USB e drivers da placa (CP210x, CH340 ou nativo USB-JTAG no S3/C3)

## Compilar e gravar

```bash
# DevKit clássico (ESP32-WROOM)
pio run -e esp32dev -t upload
pio device monitor -e esp32dev

# ESP32-S3
pio run -e esp32-s3 -t upload

# ESP32-C3
pio run -e esp32-c3 -t upload

# LilyGo T-Display-S3
pio run -e lilygo-t-display-s3 -t upload
```

O sketch inicial pisca o LED (GPIO 2 no DevKit; GPIO 38 no T-Display-S3) e imprime no Serial (115200 baud) modelo do chip, frequência da CPU e tamanho da flash.

Para mudar o pino do LED, edite `include/config.h` ou use `-DLED_GPIO=N` em `build_flags` no `platformio.ini`.

Credenciais Wi-Fi: copie `include/secrets.h.example` → `include/secrets.h`.

## Estrutura

```
esp32/
├── AGENTS.md                 instruções do agente Cursor
├── platformio.ini            ambientes das placas
├── include/config.h          pinos e intervalos
├── include/secrets.h.example modelo de segredos (não versionar secrets.h)
├── src/main.cpp              firmware
├── .cursor/environment.json  install do Cloud Agent (PlatformIO)
└── .cursor/rules/            regras do agente
```

## Agente Cursor

### Local / IDE

Abra esta pasta no Cursor. O arquivo `AGENTS.md` e `.cursor/rules/esp32-firmware.mdc` orientam o agente (PlatformIO, ambientes, segredos, estilo de commits).

### Cloud Agent

1. Publique o repositório no GitHub (seção abaixo).
2. Em [Cloud Agents](https://cursor.com/agents) → **New Agent**.
3. Selecione o repositório `avilarezende/esp32`.
4. Opcional: configure o Environment apontando para este repo (usa `.cursor/environment.json`).
5. Exemplos de prompt: “adicione Wi-Fi com reconexão”, “cliente HTTP do status PoP-SE no display”.

## Hospedagem temporária

Enquanto `avilarezende/esp32` não existir no GitHub, este projeto vive na pasta `esp32/` do repositório [conversador-pop-se](https://github.com/avilarezende/conversador-pop-se) para versionamento. O Cloud Agent dedicado deve apontar para o repositório ESP32 separado, não para o chatbot.

## Publicar como repositório próprio

Na sua máquina (com permissão de criar repos):

```bash
cd esp32
git init -b main
git add -A
git commit -m "Initial commit: ESP32 PlatformIO firmware and Cursor agent."
gh repo create avilarezende/esp32 --public --source=. --remote=origin --push
```

Ou crie o repositório vazio na interface do GitHub e faça push da pasta `esp32/` para `main`.