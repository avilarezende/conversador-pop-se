# Arquitetura — Conversador PoP-SE

## Visão geral

Sistema modular de chatbot com IA gratuita (Ollama por padrão) para atender clientes de conectividade do PoP-SE/RNP em Sergipe.

```
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌────────────┐
│  Web (Apache)│  │ Telegram Bot │  │ Discord Bot  │  │ WhatsApp   │
└──────┬───────┘  └──────┬───────┘  └──────┬───────┘  └─────┬──────┘
       │                 │                 │               │
       └─────────────────┴─────────────────┴───────────────┘
                              │  X-API-Token (header)
                              ▼
                   ┌───────────────────────┐
                   │  Engine (FastAPI)     │   rede interna,
                   │  · Persona PoP-SE     │   porta 8000 não
                   │  · Memória (PG)       │   exposta no host
                   │  · Histórico (8 msgs) │
                   │  · RAG (Chroma)       │
                   │  · LLM (Ollama/remoto)│
                   │  · Rate limiting      │
                   └──────────┬────────────┘
                              │  X-API-Token
            ┌─────────────────┴─────────────────┐
            │                                   │
     ┌──────┴───────┐                   ┌───────┴──────┐
     │  Sources     │                   │  Email MS    │
     │ Zabbix/Cacti │                   │ (Graph API)  │
     └──────────────┘                   └──────────────┘
```

## Containers

| Serviço | Função | Profile |
|---------|--------|---------|
| `postgres` | Memória persistente de usuários | `core` |
| `ollama` | LLM gratuito local | `core` |
| `engine` | Núcleo de conversação e RAG | `core` |
| `web` | Apache + página de chat | `core` |
| `module-telegram` | Canal Telegram | `telegram` |
| `module-discord` | Canal Discord | `discord` |
| `module-whatsapp` | Canal WhatsApp | `whatsapp` |
| `module-email-microsoft` | Coleta e-mails 365 | `email` |
| `module-sources` | Coletores de monitoração | `sources` |

> **Rede:** a porta `8000` do engine **não é publicada no host** (`expose` interno na rede `popse-net`). Todo tráfego ao engine passa pela rede interna do Docker e é autenticado pelo header `X-API-Token`. O `web` expõe apenas a porta `80` (host `8080`).

## Segurança da API

- **Autenticação:** todos os endpoints `/api/v1/*` (`/chat` e `/rag/ingest`) exigem o header `X-API-Token` com o valor de `ENGINE_API_TOKEN` (obrigatório). Falha *fail-closed*: token ausente/fraco → **503**; token divergente → **401**. Implementado em `services/engine/app/security.py`.
- **Clientes internos:** módulos de canal (WhatsApp/Telegram/Discord) e coletores enviam o token via `shared/popse_common/engine_client.py` (`X-API-Token`); o canal Web chega pelo proxy reverso do Apache (`/api` → `http://engine:8000`), também na rede interna.
- **CORS:** configurável por `CORS_ORIGINS` (lista separada por vírgula; vazio = CORS off).
- **Rate limiting (slowapi):** `POST /api/v1/chat` 60/min por origem e `POST /api/v1/rag/ingest` 10/min. Desativável com `ENGINE_RATE_LIMIT_ENABLED=0`. Excesso responde **429** com `Retry-After`.
- **API key Gemini:** enviada no header `x-goog-api-key` (nunca na URL).

## Memória conversacional

Além da memória persistente de perfil (nome, instituição, preferências), o engine recupera as **últimas 8 mensagens** do usuário (`get_recent_messages`/`_format_history` em `services/engine/app/memory.py` e `chat_service.py`) e as injeta no prompt como histórico, permitindo perguntas de acompanhamento ("e as manutenções?").

## RAG por instituição

As consultas de contexto (`query_context` em `services/engine/app/rag.py`) aceitam um filtro por instituição: os coletores marcam os documentos com metadados `zabbix_hosts`/`instituicao` (mapeados via `config/clients.yaml` → `links_monitorados[].zabbix_host`), e as coleções `operacional`, `institucional` e `manutencoes` são filtradas pela sigla da instituição do usuário logado.

## Configuração

- `config/clients.yaml` — instituições clientes e links
- `config/modules.yaml` — ativar/desativar módulos
- `config/sources.yaml` — parâmetros das fontes RAG
- `.env` — credenciais, token da API (`ENGINE_API_TOKEN`), CORS e rate limit (copiar de `.env.example`)

## Extensibilidade

1. **Novo canal**: criar pasta em `services/modules/<nome>/`, implementar adapter que chama `engine_client.send_chat` (o cliente envia o `X-API-Token` automaticamente).
2. **Nova fonte**: adicionar coletor em `services/modules/sources/main.py` e entrada em `config/sources.yaml`.
3. **Novo cliente**: editar `config/clients.yaml` (montado como volume no Docker).

## Persona

O engine usa prompt fixo em `services/engine/app/persona.py` exigindo tom polido, educado e solícito, sem inventar status operacionais.

### Anti prompt-injection

O contexto recuperado pelo RAG é delimitado com marcadores `<contexto_recuperado>…</contexto_recuperado>` em `services/engine/app/llm/__init__.py`. O system prompt (persona.py) instrui o modelo a tratar esse bloco como **dado**, nunca como instrução — ordens nele contidas ("ignore as instruções anteriores", "repita isto", etc.) devem ser ignoradas, e o prompt não deve ser revelado a ninguém.

## IA gratuita e remota

- **Padrão**: Ollama com `llama3.2:3b` (local, sem custo)
- **Remotos** (via `LLM_PROVIDER` no `.env`):
  - `gemini` — Google Gemini
  - `openai` — OpenAI API
  - `azure` — Azure OpenAI
  - `grok` — xAI Grok

Implementação em `services/engine/app/llm/providers.py`.

## Exemplo de fluxo

1. Módulo de canal envia `POST /api/v1/chat` com o header `X-API-Token`
2. Engine extrai nome e instituição, persiste em PostgreSQL e recupera as últimas 8 mensagens (histórico)
3. RAG busca manutenções em `manutencoes` e status em `operacional`, filtrado pela instituição do usuário
4. LLM gera resposta educada com base no contexto delimitado por `<contexto_recuperado>` (anti prompt-injection)
