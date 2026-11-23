# Ví

**Comunicação segura ancorada em relações reais, entidades reconhecidas e integridade criptográfica.**

Ví é um aplicativo de mensagens (texto, voz e vídeo) focado em **segurança** e **integridade**: ninguém conversa “no vazio” — toda interação exige um **vínculo válido** no grafo de relações, tipicamente associado a um **local ou evento real**, e mediado ou autorizado por uma **entidade reconhecida**.

---

## Abertura: docs sim, código não

| Artefato | Política |
|----------|----------|
| Documentação de **conceito e lógica** (`docs/`) | **Publicável** — ver [docs/LICENCA-DOCUMENTACAO.md](docs/LICENCA-DOCUMENTACAO.md) |
| **Código-fonte** da aplicação (`packages/`, `apps/`, builds, secrets) | **Proprietário / fechado** |

Bibliotecas de terceiros (ex.: liboqs para PQC) mantêm as licenças dos respectivos projetos; isso não torna o código do Ví open-source.

---

## Em uma frase

Mensageiro com grafo de confiança (máx. 2 arestas em convites indivíduo–indivíduo; entidades reconhecidas sem esse teto), ledger criptografado por conversa, marca d’água em mídia exportada, chaves por conversa ligadas ao hardware e comunicação **sempre ponto a ponto**.

---

## Documentação

Índice completo: **[docs/INDEX.md](docs/INDEX.md)**

| Documento | Conteúdo |
|-----------|----------|
| [docs/00-conceito.md](docs/00-conceito.md) | Visão de produto |
| [docs/01-modelo-relacoes.md](docs/01-modelo-relacoes.md) | Grafo e regras de contato |
| [docs/02-ledger-e-midia.md](docs/02-ledger-e-midia.md) | Ledger e marca d’água |
| [docs/03-criptografia-pqc.md](docs/03-criptografia-pqc.md) | Modelo PQC (libs livres; app fechado) |
| [docs/04-arquitetura.md](docs/04-arquitetura.md) | Monólito modular + hexagonal |
| [docs/06-chaves-hardware-e-ui.md](docs/06-chaves-hardware-e-ui.md) | Soft-delete UI; chaves × hardware |
| [docs/07-implementacao-hexagonal.md](docs/07-implementacao-hexagonal.md) | Como implementar; N módulos |
| [docs/08-fluxo-dados.md](docs/08-fluxo-dados.md) | Fluxo de dados |
| [docs/09-fluxo-comunicacao-p2p.md](docs/09-fluxo-comunicacao-p2p.md) | Comunicação P2P |
| [docs/10-diagrama-classes.md](docs/10-diagrama-classes.md) | Diagrama de classes |
| [docs/11-diagramas-fluxo.md](docs/11-diagramas-fluxo.md) | Diagramas de fluxo |
| [docs/12-implantacao.md](docs/12-implantacao.md) | Implantação |

---

## Padrão de projeto

**Monólito modular + Arquitetura Hexagonal (Ports & Adapters) + bounded contexts.**

Escala além de 6 módulos: novos pacotes + ports + feature flags — detalhes em [docs/07-implementacao-hexagonal.md](docs/07-implementacao-hexagonal.md).

---

## Estrutura

```
vi/
├── docs/                 # Conceito e lógica (publicável)
├── packages/             # Domínio (código proprietário)
├── apps/                 # API / mobile / web (proprietário)
├── config/
├── pyproject.toml
└── docker-compose.yml
```

## Explorar o esqueleto (dev)

```bash
cd vi   # ou raiz deste repositório, se standalone
pip install -e ".[dev]"
PYTHONPATH=packages:apps/api python -m pytest -q
uvicorn vi_api.main:app --app-dir apps/api --reload
```

## Princípios não negociáveis

- Sem vínculo válido, sem canal.
- Conteúdo sempre **P2P** (servidor sem plaintext).
- Ledger append-only; apagar/editar na UI não apaga o ledger.
- Chave por conversa ligada ao hardware; rotação parcial proibida.
- PQC via bibliotecas auditáveis de código livre; produto Ví fechado.
