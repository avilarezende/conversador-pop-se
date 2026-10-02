# Guia de configuração

Referência de todos os arquivos e variáveis que precisam ser preenchidos antes do deploy.

## Arquivos de configuração

| Arquivo | Montado no Docker? | O que preencher |
|---------|-------------------|-----------------|
| `.env` | Sim (via `env_file`) | Credenciais e escolha do provedor LLM |
| `config/clients.yaml` | Sim (volume) | Instituições clientes e links monitorados |
| `config/modules.yaml` | Sim | Módulos ativos (canais e fontes RAG) |
| `config/sources.yaml` | Sim | Parâmetros não sensíveis das fontes |

## Provedor de IA (`LLM_PROVIDER`)

| Valor | Quando usar | Variáveis obrigatórias |
|-------|-------------|------------------------|
| `ollama` | Desenvolvimento, sem custo, on-premise | `OLLAMA_HOST`, `OLLAMA_MODEL` |
| `gemini` | Produção leve com tier gratuito Google | `GEMINI_API_KEY` |
| `openai` | Produção com modelos OpenAI | `OPENAI_API_KEY` |
| `azure` | Ambiente corporativo Microsoft | `AZURE_OPENAI_*` (todas) |
| `grok` | Modelos xAI Grok | `GROK_API_KEY` |

Altere `LLM_PROVIDER` no `.env` e reinicie o container `engine`.

> **Gemini:** a `GEMINI_API_KEY` é enviada no header `x-goog-api-key` (não mais na URL), evitando vazamento da chave em logs e proxies.

## Segurança da API do engine

### Token interno (`ENGINE_API_TOKEN`) — obrigatório

Todos os endpoints `/api/v1/*` (`/api/v1/chat` e `/api/v1/rag/ingest`) exigem o header `X-API-Token` com o valor de `ENGINE_API_TOKEN`. O engine falha de forma *fail-closed*:

- Com `ENGINE_API_TOKEN` ausente ou fraco (`change-me-engine-token`, `secret`, etc.), a API recusa com **HTTP 503**.
- Com token presente mas divergente, recusa com **HTTP 401** (`token de API inválido`).

Gere um token forte e use o mesmo valor no engine e em todos os módulos:

```bash
openssl rand -hex 32
```

No `.env`:

```
ENGINE_API_TOKEN=seudotokenhexforte...   # ex.: openssl rand -hex 32
```

Os módulos de canal (WhatsApp, Telegram, Discord) e os coletores enviam o token automaticamente via `shared/popse_common/engine_client.py`. `ENGINE_ALLOW_WEAK_TOKEN=1` pode ser usado apenas em desenvolvimento local.

### CORS (`CORS_ORIGINS`)

| Variável | Descrição |
|----------|-----------|
| `CORS_ORIGINS` | Origens permitidas no engine, separadas por vírgula. Vazio/ausente = **CORS desativado**. Ex.: `https://painel.pop-se.rnp.br,https://chat.pop-se.rnp.br` |

### Rate limiting (slowapi)

O engine limita requisições por origem (IP) com `slowapi`:

| Endpoint | Limite |
|----------|--------|
| `POST /api/v1/chat` | 60/minuto |
| `POST /api/v1/rag/ingest` | 10/minuto |

Excesso retorna **HTTP 429**. Para desativar em testes/desenvolvimento:

```
ENGINE_RATE_LIMIT_ENABLED=0
```

## Fontes de monitoração

### Zabbix

| Variável | Descrição |
|----------|-----------|
| `ZABBIX_URL` | URL base do servidor (ex.: `https://zabbix.pop-se.rnp.br`) |
| `ZABBIX_USER` | Usuário com permissão de API |
| `ZABBIX_PASSWORD` | Senha do usuário |
| `ZABBIX_MAINTENANCE_DAYS` | Quantos dias à frente buscar manutenções (padrão: 30) |

Ative em `config/modules.yaml` → `fontes_rag.zabbix.enabled: true` e suba `--profile sources`.

> **RAG por instituição:** o coletor Zabbix marca os documentos com metadados `zabbix_hosts` (hosts afetados) e `instituicao` (sigla mapeada via `config/clients.yaml` → `links_monitorados[].zabbix_host`). Assim, as consultas de manutenções e status são filtradas pela instituição do usuário logado.

### Cacti

| Variável | Descrição |
|----------|-----------|
| `CACTI_URL` | URL base do Cacti |
| `CACTI_USER` | Usuário web com acesso a hosts/gráficos |
| `CACTI_PASSWORD` | Senha |

### Grafana

| Variável | Descrição |
|----------|-----------|
| `GRAFANA_URL` | URL base do Grafana |
| `GRAFANA_API_KEY` | Service Account Token com leitura de alertas/anotações |
| `GRAFANA_ANNOTATION_DAYS` | Janela de anotações em dias |

## Instituições (`config/clients.yaml`)

Para cada instituição conectada ao PoP-SE:

```yaml
- sigla: SIGLA          # identificador curto (IFS, UFS...)
  nome: "Nome completo"
  aliases: [...]        # como o usuário pode se referir
  links_monitorados:
    - zabbix_host: "..." # deve existir no Zabbix
```

## Checklist de deploy

- [ ] `.env` criado a partir de `.env.example`
- [ ] `POSTGRES_PASSWORD` alterado
- [ ] `ENGINE_API_TOKEN` gerado com `openssl rand -hex 32` (igual no engine e módulos)
- [ ] `LLM_PROVIDER` definido e API key configurada (se remoto)
- [ ] `config/clients.yaml` com instituições reais
- [ ] Fontes necessárias habilitadas em `config/modules.yaml`
- [ ] Credenciais Zabbix/Cacti/Grafana no `.env` (se aplicável)
- [ ] `docker compose --profile core --profile sources up -d`

## Logos

Os logos oficiais foram obtidos de https://www.pop-se.rnp.br:

- `services/web/public/assets/logo-popse.png` — PoP-SE PRO RNP
- `services/web/public/assets/logo-rnp.png` — RNP

Fonte: `/assets/img/POP_SE_PRORNP_RGB_PNG.png` e `/assets/img/rnp-logo-pegb.png`
