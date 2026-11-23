# Vínculo

**Comunicação segura ancorada em relações reais, entidades reconhecidas e integridade criptográfica.**

Vínculo é um aplicativo de mensagens (texto, voz e vídeo) focado em **segurança** e **integridade**: ninguém conversa “no vazio” — toda interação exige um **vínculo válido** no grafo de relações, tipicamente associado a um **local ou evento real**, e mediado ou autorizado por uma **entidade reconhecida**.

> Este diretório (`vinculo/`) é uma iniciativa **nova e independente** do chatbot Conversador PoP-SE na raiz do repositório. Aqui há apenas planejamento, conceito e esqueleto modular — sem implementação completa de produção.

---

## Em uma frase

Mensageiro estilo WhatsApp com grafo de confiança (máx. 2 saltos), ledger criptografado por conversa, marca d’água em mídia exportada e criptografia pós-quântica de código aberto.

---

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| [docs/00-conceito.md](docs/00-conceito.md) | Visão de produto, princípios e personas |
| [docs/01-modelo-relacoes.md](docs/01-modelo-relacoes.md) | Grafo, entidades, locais/eventos, regras de contato |
| [docs/02-ledger-e-midia.md](docs/02-ledger-e-midia.md) | Ledger por conversa, mídia e marca d’água |
| [docs/03-criptografia-pqc.md](docs/03-criptografia-pqc.md) | PQC open-source, voz/vídeo, ameaça |
| [docs/04-arquitetura.md](docs/04-arquitetura.md) | Padrão escolhido, módulos, ports & adapters |
| [docs/05-roadmap.md](docs/05-roadmap.md) | Fases sugeridas e critérios de pronto |

---

## Padrão de projeto escolhido

**Monólito modular + Arquitetura Hexagonal (Ports & Adapters) + contextos delimitados (DDD leve).**

Por quê:

1. Domínios distintos (grafo, ledger, mídia, A/V, crypto) precisam de limites claros sem o custo operacional de microsserviços no dia 1.
2. Novas funcionalidades entram como **módulos/plugins** com contratos (`ports`), sem acoplar o núcleo.
3. Adaptadores (SQLite/Postgres, liboqs, WebRTC, armazenamento de objetos) são substituíveis.
4. Extrair um módulo para serviço dedicado depois permanece viável (mesmos ports).

Detalhes: [docs/04-arquitetura.md](docs/04-arquitetura.md).

---

## Estrutura do esqueleto

```
vinculo/
├── docs/                         # Planejamento e conceito
├── packages/                     # Bibliotecas de domínio (Python)
│   ├── vinculo_core/             # Tipos, erros, eventos de domínio
│   ├── vinculo_identity/         # Identidade e chaves
│   ├── vinculo_trust_graph/      # Grafo de relações e políticas
│   ├── vinculo_ledger/           # Ledger criptografado por conversa
│   ├── vinculo_media/            # Importação, exportação, marca d’água
│   ├── vinculo_realtime/         # Sessões de voz/vídeo (contratos)
│   └── vinculo_crypto_pqc/       # Fachada PQC (liboqs / alternativas)
├── apps/
│   ├── api/                      # Composição FastAPI dos módulos
│   ├── mobile/                   # Esqueleto do cliente móvel (Flutter)
│   └── web/                      # Esqueleto do cliente web
├── config/                       # Feature flags e módulos
├── pyproject.toml                # Workspace Python (uv/pip)
└── docker-compose.yml            # Núcleo local (API + Postgres + MinIO)
```

---

## Como explorar o esqueleto

```bash
cd vinculo
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest
uvicorn vinculo_api.main:app --app-dir apps/api --reload
```

---

## Princípios não negociáveis

- **Sem vínculo válido, sem canal.** Contato só com 1º grau, ou até 2 saltos com entidade reconhecida como ponte/autorizadora.
- **Ledger por conversa.** Texto e mídia da conversa vivem em cadeia append-only criptografada, isolada de outras mídias do aparelho.
- **Exportação rastreável.** Toda mídia interna exportada leva marca d’água e metadados do responsável/criador.
- **PQC open-source.** Troca de chaves e assinaturas com algoritmos pós-quânticos de código livre (ex.: ML-KEM / ML-DSA via liboqs).
- **Modularidade.** Features novas = novo pacote + adapter, não “mais um if” no núcleo.
