# Agente ESP32-CYD (Calisto + Grok)

Você é o agente deste repositório **standalone**. Não há relação com Conversador PoP-SE nem com outros monorepos.

Trabalhe em **português** com o usuário; código, identificadores e commits em inglês quando for o padrão técnico.

## Escopo

- Firmware **ESP32 Cheap Yellow Display (CYD / ESP32-2432S028)** — PlatformIO + Arduino.
- Avatar **Calisto** na tela (toque + chips + Serial).
- Chat direto com a API **xAI Grok** (`api.x.ai`), sem backend intermediário.
- Simulador web em `simulator/` para validar UX sem hardware.
- Ambiente Cloud Agent: `.cursor/environment.json` (nome **esp32**).

## Agentes especializados

| Arquivo | Papel |
|---------|--------|
| `agents/firmware.md` | Build PlatformIO, pinout CYD, Wi-Fi, cliente Grok |
| `agents/ux-avatar.md` | Layout 320×240, animações do avatar, toque |

Leia o agente especializado quando a tarefa for claramente de firmware ou de UX.

## Ambientes PlatformIO

| Env | Uso |
|-----|-----|
| `cyd` | ESP32-2432S028 com LED GPIO 4 |
| `cyd-noled` | Mesmo hardware sem LED |

## Regras

1. Segredos só em `include/secrets.h` (gitignored) a partir de `secrets.h.example`.
2. Nunca versionar `.pio/`, binários, `secrets.h`, `.env` ou chaves Grok.
3. Manter `src/main.cpp` enxuto; lógica nova em módulos.
4. Respostas do Grok curtas (prompt de sistema já pede isso) — cabem no balão.
5. Commits: inglês imperativo (`Add avatar blink`, `Fix CYD touch map`).

## Comandos

```bash
pio run -e cyd
pio run -e cyd -t upload
pio device monitor -e cyd
python3 tests/test_grok_contract.py
cd simulator && python3 -m http.server 8765
```

## Cloud Agent

`.cursor/environment.json` instala PlatformIO. Após o boot: `export PATH="$HOME/.local/bin:$PATH"`.
