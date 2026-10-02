# Changelog — Conversador PoP-SE

Registro das principais atualizações e correções. Datas no formato AAAA-MM.

## v0.2.0 — Assistente Calisto, guardrails e administração

Entrega do PR [#21](https://github.com/avilarezende/conversador-pop-se/pull/21).

### Novidades

- **Mascote Calisto**: assistente ganhou identidade visual como papagaio
  ring-neck verde, com **avatar flutuante animado** (estados idle/pensando/
  falando) e fundo transparente. Nome "Calisto" em toda a interface.
- **Refatoração de UX/acessibilidade (WCAG AA)**: landmarks semânticos, skip
  link, foco visível, rótulos/`aria-live`, contraste AA, indicador de digitação,
  `textarea` auto-crescente, envio com Enter seguro para IME (`Shift+Enter`
  quebra linha), suporte a `prefers-reduced-motion` e layout responsivo.
- **Guardrails de escopo**: camada determinística que mantém o Calisto restrito
  ao PoP-SE/RNP, avaliada antes de acionar a IA (regras de `scope` e de
  `blocked_keywords`), com orientação de escopo no prompt do sistema.
- **Painel de administração** (`/admin.html`, protegido por `ADMIN_TOKEN`):
  - selecionar **provedor de IA e modelo** (Ollama/Gemini/OpenAI/Azure/Grok,
    pré-configurados) e informar **API keys** (gravadas com segurança,
    exibidas mascaradas);
  - **criar/ativar/excluir guardrails**;
  - **gerenciar a base de conhecimento (RAG)**: adicionar/editar/excluir
    documentos das coleções `operacional`, `institucional` e `manutencoes`.
- **API de administração**: `GET /api/v1/admin/config`, `PUT /api/v1/admin/llm`,
  `GET/POST/PATCH/DELETE /api/v1/admin/guardrails`, `GET /api/v1/admin/rag/collections`
  e `GET/POST/DELETE /api/v1/admin/rag/documents`.

### Correções

- **Engine não iniciava**: `services/engine/app/rag.py` avaliava
  `chromadb.PersistentClient | None` como tipo no import (no `chromadb` 0.6.3
  `PersistentClient` é função de fábrica), quebrando a inicialização. Resolvido
  com `from __future__ import annotations`.
- **Modelo Gemini padrão**: `gemini-1.5-flash` foi descontinuado (404);
  atualizado para `gemini-flash-latest` em `config.py`, `docker-compose.yml` e
  `.env.example`.
- **Lint (ruff)**: corrigidos apontamentos pré-existentes (imports não usados,
  ordenação de imports, linhas longas).
- **Avatar flutuante**: fundo transparente e sem sobreposição do balão de
  status durante a animação; tamanho aumentado em 50%.

### Documentação

- Manuais atualizados (README, ARCHITECTURE, CONFIGURATION, MODULES) com
  Calisto, administração, guardrails e RAG, além de capturas de tela em
  `docs/img/`.

### Integração com a base (`main`)

Este trabalho foi mesclado com os avanços de segurança/plataforma já presentes
no `main`, combinando as intenções sem perda de funcionalidade:

- **Autenticação entre serviços** no engine via header `X-API-Token`
  (`ENGINE_API_TOKEN`) — distinta do `X-Admin-Token` da administração.
- **Anti prompt-injection**: contexto recuperado delimitado por
  `<contexto_recuperado>`.
- **Memória conversacional**: histórico das últimas 8 mensagens no contexto.
- **RAG por instituição**: busca filtrada pela instituição do usuário.
- **Rate limiting** nos endpoints do engine e job de **security-scan** no CI.
