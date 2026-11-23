# Fluxo de dados — Ví

## Princípio

Dados de **conteúdo** (mensagens, mídia, áudio/vídeo) circulam e persistem sob controle dos **pares** (P2P + ledger local/replicado entre participantes). O servidor de coordenação, se existir, trata **metadados mínimos** (grafo, sinalização, presença), nunca plaintext da conversa.

## Visão geral

```mermaid
flowchart LR
  subgraph DeviceA["Dispositivo A"]
    UIA[UI]
    KA["K_A,C + HW binding"]
    LA[Ledger C]
    MA[Cofre mídia C]
  end

  subgraph DeviceB["Dispositivo B"]
    UIB[UI]
    KB["K_B,C + HW binding"]
    LB[Ledger C]
    MB[Cofre mídia C]
  end

  subgraph Coord["Coordenação - sem plaintext"]
    SG[Sinalização / discovery]
    GR[Metadados de grafo]
  end

  UIA -->|append cifrado| LA
  UIA -->|P2P ciphertext| UIB
  UIB -->|append cifrado| LB
  LA -.->|sync criptografada entre pares| LB
  MA -.->|blob cifrado P2P| MB
  DeviceA --> SG
  DeviceB --> SG
  DeviceA --> GR
  DeviceB --> GR
  KA --- LA
  KB --- LB
```

## Categorias de dados

| Categoria | Onde vive | Quem lê |
|-----------|-----------|---------|
| Entradas do ledger (ciphertext) | Dispositivos dos participantes (+ réplica opcional cifrada) | Só com `K_{U,C}` dos envolvidos |
| Projeção UI (ocultar/editar) | Preferências locais do usuário | Só o dono da UI |
| Grafo (arestas, âncoras) | Coordenação + cache local | Política de minimização |
| Chaves `K_{U,C}` | Secure element / keystore do hardware | Só o usuário U no device atual |
| Mídia exportada | Fora do cofre, com WM + metadados | Quem recebe o arquivo |

## Soft-delete / edição (só UI)

```mermaid
sequenceDiagram
  participant U as Usuário
  participant UI as UI local
  participant L as Ledger C

  U->>UI: Apagar conversa / editar msg
  UI->>UI: Atualiza projeção (ocultar)
  UI->>L: append ui_hide_* ou message_correction
  Note over L: Cadeia e ciphertext originais permanecem
  U->>UI: Recuperar conversa individual
  UI->>L: Rematerializa entradas se K_A,C e K_B,C ok
```

## Dados que NÃO atravessam o servidor em claro

- Corpo de mensagem
- Bytes de mídia do cofre
- Áudio/vídeo da chamada
- Chaves de conversa ou épocas

Ver também: [09-fluxo-comunicacao-p2p.md](09-fluxo-comunicacao-p2p.md), [06-chaves-hardware-e-ui.md](06-chaves-hardware-e-ui.md).
