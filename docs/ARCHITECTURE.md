# Arquitetura — Conversador PoP-SE

## Visão geral

Sistema modular de chatbot com IA gratuita (Ollama por padrão) para atender clientes de conectividade do PoP-SE/RNP em Sergipe.

```
┌─────────────┐  ┌──────────────┐  ┌──────────────┐
│  Web (Apache)│  │ Telegram Bot │  │ Discord Bot  │  ... canais
└──────┬──────┘  └──────┬───────┘  └──────┬───────┘
       │                │                  │
       └────────────────┼──────────────────┘
                        ▼
              ┌──────────────────┐
              │  Engine (FastAPI) │
              │  - Persona Calisto│
              │  - Guardrails     │
              │  - Memória (PG)   │
              │  - RAG (Chroma)   │
              │  - LLM (Ollama…)  │
              │  - Admin API      │
              └────────┬─────────┘
                       ▲
       ┌───────────────┼───────────────┐
       │               │               │
┌──────┴──────┐ ┌──────┴──────┐ ┌─────┴─────┐
│ Email MS    │ │ Sources     │ │ WhatsApp  │
│ (Graph API) │ │ Zabbix/Cacti│ │ Webhook   │
└─────────────┘ └─────────────┘ └───────────┘
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

## Configuração

- `config/clients.yaml` — instituições clientes e links
- `config/modules.yaml` — ativar/desativar módulos
- `config/sources.yaml` — parâmetros das fontes RAG
- `.env` — credenciais (copiar de `.env.example`)

## Extensibilidade

1. **Novo canal**: criar pasta em `services/modules/<nome>/`, implementar adapter que chama `engine_client.send_chat`.
2. **Nova fonte**: adicionar coletor em `services/modules/sources/main.py` e entrada em `config/sources.yaml`.
3. **Novo cliente**: editar `config/clients.yaml` (montado como volume no Docker).

## Persona e guardrails

O engine usa prompt fixo em `services/engine/app/persona.py` exigindo tom polido, educado e solícito, sem inventar status operacionais. O assistente é o **Calisto** (mascote papagaio ring-neck verde).

Antes de acionar a IA, `services/engine/app/guardrails.py` avalia a mensagem contra regras de escopo (`scope`) e palavras bloqueadas (`blocked_keywords`); mensagens fora do escopo do PoP-SE/RNP recebem uma recusa educada e não chegam ao LLM.

## Administração (runtime)

`services/engine/app/routers/admin.py` expõe a API `/api/v1/admin` (protegida por `X-Admin-Token`) para configurar, sem reiniciar:

- **provedor de IA / modelo / API keys** (aplicados via `settings_store.apply_overrides`);
- **guardrails** (CRUD);
- **base de conhecimento RAG** (documentos das coleções).

As configurações são persistidas por `services/engine/app/settings_store.py` (arquivo JSON em `ADMIN_STORE_PATH`). A interface está em `services/web/public/admin.html`.

## IA gratuita e remota

- **Padrão**: Ollama com `llama3.2:3b` (local, sem custo)
- **Remotos** (via `LLM_PROVIDER` no `.env`):
  - `gemini` — Google Gemini
  - `openai` — OpenAI API
  - `azure` — Azure OpenAI
  - `grok` — xAI Grok

Implementação em `services/engine/app/llm/providers.py`.

## Exemplo de fluxo

1. Usuário: "Bom dia, sou Rodrigo. Sou responsável técnico pelo IFS..."
2. Engine extrai nome e instituição, persiste em PostgreSQL
3. Guardrails validam o escopo da mensagem (recusa educada se fora do PoP-SE/RNP)
4. RAG busca manutenções em `manutencoes` e status em `operacional`
5. LLM (provedor/modelo definidos no `.env` ou na administração) gera resposta educada com base no contexto recuperado
