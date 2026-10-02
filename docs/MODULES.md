# Módulos — Conversador PoP-SE

## Autenticação contra o engine

Os módulos de canal (WhatsApp, Telegram, Discord) e os coletores chamam a API do engine pelos helpers de `shared/popse_common/engine_client.py` (`send_chat`/`ingest_rag`), que enviam automaticamente o header `X-API-Token` com o valor de `ENGINE_API_TOKEN`. O token deve ser o **mesmo** definido no `.env` do engine, senão as chamadas `/api/v1/*` são recusadas (HTTP 401/503).

O canal **Web** não passa pelo `engine_client`: o Apache do container `web` faz o proxy reverso de `/api` → `http://engine:8000/api` pela rede interna (`popse-net`), e o engine exige o mesmo `X-API-Token` nesses endpoints.

## Canais

| Módulo | Ativação | Variáveis |
|--------|----------|-----------|
| Web | `core` (padrão) | — |
| Telegram | `docker compose --profile telegram up` | `TELEGRAM_BOT_TOKEN` |
| Discord | `--profile discord` | `DISCORD_BOT_TOKEN` |
| WhatsApp | `--profile whatsapp` | `WHATSAPP_API_URL`, `WHATSAPP_API_TOKEN` |

## Fontes RAG

| Fonte | Status | Método |
|-------|--------|--------|
| Site PoP-SE | Implementado | HTTP crawler |
| Zabbix | **Implementado** | JSON-RPC API (manutenções + problemas) |
| Cacti | **Implementado** | Login web + extração hosts/gráficos |
| Grafana | **Implementado** | API (anotações + alertas) |
| E-mail Microsoft | Implementado | Graph API |
| MRTG | Stub | — |
| Topdesk | Stub | — |

### RAG por instituição

Os coletores marcam os documentos com metadados de contexto institucional:

- **Zabbix** (`services/modules/sources/collectors/zabbix.py`) registra `zabbix_hosts` (hosts afetados) e `instituicao` (sigla deduzida pelo mapeamento em `config/clients.yaml` → `links_monitorados[].zabbix_host`).
- `query_context` no engine filtra as coleções `operacional`/`institucional`/`manutencoes` pela sigla da instituição do usuário logado, dando prioridade ao filtro por hosts quando disponível.

Para habilitar coletores:

```bash
docker compose --profile core --profile sources up -d
docker compose --profile core --profile email up -d
```

## Adicionar nova fonte

1. Registrar em `config/modules.yaml` → `fontes_rag`
2. Adicionar bloco em `config/sources.yaml`
3. Implementar função `collect_<nome>()` em `services/modules/sources/main.py`
4. Mapear para coleção RAG: `operacional`, `institucional` ou `manutencoes`
5. Se a fonte for por instituição, marcar os metadados `zabbix_hosts`/`instituicao`

## Gerenciar documentos RAG manualmente

Além dos coletores automáticos, os documentos das coleções `operacional`,
`institucional` e `manutencoes` podem ser adicionados/editados/excluídos pelo
painel de administração (`/admin.html` → **Base de conhecimento (RAG)**), sem
depender de um coletor. Cada documento tem identificador, fonte e conteúdo.

## Guardrails

O Calisto é mantido no escopo do PoP-SE/RNP por guardrails avaliados antes da
IA (regras de escopo e de palavras bloqueadas). São gerenciados no painel de
administração e implementados em `services/engine/app/guardrails.py`.
