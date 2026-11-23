# Conceito — Vínculo

## Problema

Mensageiros populares otimizam alcance e conveniência: qualquer número ou link pode abrir um canal. Isso facilita spam, engenharia social, vazamento de mídia sem rastreio e confiança frágil entre desconhecidos.

## Proposta

**Vínculo** inverte a premissa: a comunicação é um **efeito colateral de uma relação válida no mundo real** — pessoa a pessoa, pessoa a entidade, ou pessoa–pessoa autorizada por entidade — tipicamente **ancorada a um local ou evento** (congresso, campus, hospital, operação de campo, assembleia).

Não é “mais um chat com E2EE”. É um sistema em que:

1. **Quem pode falar com quem** é decidido por um **grafo de relações** com regras explícitas.
2. **O que foi dito/enviado** vive em um **ledger criptografado por conversa**.
3. **O que sai do cofre** (exportação de mídia) carrega **marca d’água e metadados de responsabilidade**.
4. **Como se protege o canal** usa **criptografia pós-quântica de código aberto**, inclusive para voz e vídeo.

## Princípios de produto

| Princípio | Significado prático |
|-----------|---------------------|
| Ancoragem | Relação preferencialmente ligada a local/evento real |
| Menor privilégio social | Contato direto (1º grau) por padrão; 2 saltos só com ponte válida |
| Entidade como âncora de confiança | Instituições/organizações reconhecidas podem contactar e autorizar pares |
| Integridade > conveniência | Preferir bloquear a conversa a permitir canal ambíguo |
| Separação de cofres | Ledger da conversa ≠ galeria do aparelho |
| Rastreabilidade ética | Exportação identifica responsável sem expor o plaintext no servidor |
| Cripto auditável | Algoritmos PQC open-source; sem caixa-preta proprietária no núcleo |

## Personas

- **Indivíduo** — cidadão, pesquisador, profissional que só fala com quem o grafo autoriza.
- **Entidade reconhecida** — universidade, hospital, órgão, empresa auditada; pode contactar membros e **autorizar** relação entre dois indivíduos que a reconhecem.
- **Operador de evento/local** — cria âncoras temporárias (ex.: “Workshop X, 12–14 nov”) que limitam o escopo das arestas.
- **Auditor de integridade** — verifica cadeia do ledger e metadados de mídia exportada (sem necessariamente ler conteúdo).

## Experiência-alvo (resumo)

1. Usuário se identifica e registra chaves (incluindo PQC).
2. Estabelece reconhecimento mútuo com uma **entidade** e/ou contato de **1º grau** (presença, QR no evento, convite assinado).
3. Para falar com alguém a 2 saltos, precisa de caminho no grafo com entidade reconhecida pelos envolvidos.
4. Mensagens e mídias vão ao **ledger da conversa**; a galeria do celular permanece isolada.
5. Exportar mídia aplica marca d’água + metadados do criador/responsável.
6. Chamada de voz/vídeo usa canal E2EE com handshake PQC.

## O que Vínculo deliberadamente *não* é

- Rede social aberta ou discovery global de desconhecidos.
- “Blockchain pública” de conteúdo legível — o ledger é **por conversa**, criptografado, append-only.
- Substituição de identidade civil governamental (pode integrar IdPs no futuro via adapter).
