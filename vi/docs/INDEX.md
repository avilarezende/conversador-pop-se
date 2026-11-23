# Documentação do Ví — índice

Visão geral do mensageiro **Ví**: conceito, arquitetura hexagonal modular, fluxos ponto a ponto, classes, implantação e integridade.

> **Política:** esta documentação (conceito e lógica) é **publicável**. O código-fonte da aplicação é **proprietário**. Ver [LICENCA-DOCUMENTACAO.md](LICENCA-DOCUMENTACAO.md).

## Conceito e regras de negócio

| Doc | Conteúdo |
|-----|----------|
| [00-conceito.md](00-conceito.md) | Visão de produto, princípios, personas |
| [01-modelo-relacoes.md](01-modelo-relacoes.md) | Grafo, entidades, limite de arestas (só indivíduo–indivíduo) |
| [02-ledger-e-midia.md](02-ledger-e-midia.md) | Ledger append-only, cofres, marca d’água |
| [03-criptografia-pqc.md](03-criptografia-pqc.md) | PQC open-source, voz/vídeo |
| [06-chaves-hardware-e-ui.md](06-chaves-hardware-e-ui.md) | Soft-delete/edição só na UI; chaves por conversa + hardware |

## Arquitetura e implementação

| Doc | Conteúdo |
|-----|----------|
| [04-arquitetura.md](04-arquitetura.md) | Padrão escolhido (monólito modular + hexagonal) |
| [07-implementacao-hexagonal.md](07-implementacao-hexagonal.md) | Como implementar; escalar além de 6 módulos |
| [05-roadmap.md](05-roadmap.md) | Fases |

## Fluxos e diagramas

| Doc | Conteúdo |
|-----|----------|
| [08-fluxo-dados.md](08-fluxo-dados.md) | Fluxo de dados (ledger, mídia, chaves, UI) |
| [09-fluxo-comunicacao-p2p.md](09-fluxo-comunicacao-p2p.md) | Comunicação **sempre ponto a ponto** |
| [10-diagrama-classes.md](10-diagrama-classes.md) | Diagrama de classes (domínio + ports) |
| [11-diagramas-fluxo.md](11-diagramas-fluxo.md) | Sequências: abrir canal, mensagem, mídia, rotação HW |
| [12-implantacao.md](12-implantacao.md) | Esquema de implantação e topologia |

## Política e roadmap

| Doc | Conteúdo |
|-----|----------|
| [LICENCA-DOCUMENTACAO.md](LICENCA-DOCUMENTACAO.md) | Docs abertas × código fechado |
| [05-roadmap.md](05-roadmap.md) | Fases |

## Convenções dos diagramas

- Diagramas em **Mermaid** (renderizam no GitHub e em muitos viewers Markdown).
- Comunicação de conteúdo de conversa: **P2P** (sem plaintext no servidor de coordenação).
- Servidor de coordenação: descoberta, metadados de grafo minimizados, sinalização — **não** é hub de mensagens.
