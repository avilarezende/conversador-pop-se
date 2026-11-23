# Roadmap sugerido

Escopo deste entregável: **fase 0** (conceito + esqueleto). As fases seguintes são orientação — não comprometem implementação neste PR.

## Fase 0 — Planejamento e esqueleto *(atual)*

- [x] Conceito e princípios
- [x] Modelo de grafo e regras R1–R4
- [x] Ledger + mídia + marca d’água (especificação)
- [x] Estratégia PQC open-source
- [x] Padrão modular hexagonal
- [x] Pacotes, ports, API stub, clientes stub, testes de política

## Fase 1 — Núcleo de confiança e mensagens

- Persistência real do grafo e decisões `can_open_channel`
- Ledger append-only em disco com verificação de cadeia
- Identidade local + pares de chaves (mock → liboqs)
- Cliente móvel: onboarding, contatos 1º grau, chat texto

## Fase 2 — Mídia e exportação

- Importação da galeria → cofre da conversa
- Pipeline de marca d’água + metadados + `export_event`
- Blob store criptografado

## Fase 3 — Tempo real

- Sinalização autenticada
- WebRTC com E2EE; evolução hybrid PQC no handshake
- Feature flag `realtime_av`

## Fase 4 — Entidades, âncoras e operação

- Painel web para entidades reconhecidas
- Emissão de `autoriza_par` e âncoras de evento/local
- Revogação, expiração, auditoria de exportações

## Fase 5 — Endurecimento

- Multi-dispositivo, backup, threat model formal
- SBOM crypto, fuzzing de parsers de mídia
- Avaliação de proofs de caminho / minimização de metadados

## Critérios de pronto (definição de “funciona”)

Um incremento só é “pronto” se:

1. A política de grafo for testável sem UI.
2. O ledger verificar encadeamento após crash simulado.
3. Exportação sem watermark for impossível no caminho feliz e no caminho de erro.
4. Novos módulos entrarem via `config/modules.yaml` + pacote, sem editar regras de outros contextos.
