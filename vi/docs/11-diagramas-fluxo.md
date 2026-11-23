# Diagramas de fluxo — Ví

Sequências operacionais principais (conceito/lógica).

## 1. Autorizar e abrir canal

```mermaid
flowchart TD
  Start([Pedido A↔B]) --> Same{A = B?}
  Same -->|sim| Deny[NO_VALID_PATH / SAME_NODE]
  Same -->|não| Ent{Um lado é entidade?}
  Ent -->|sim| Rec{Indivíduo reconhece entidade?}
  Rec -->|sim| AllowE[ENTITY_TO_INDIVIDUAL]
  Rec -->|não| Deny
  Ent -->|não| Direct{contato_direto mútuo?}
  Direct -->|sim| Allow1[DIRECT_1ST_DEGREE]
  Direct -->|não| Path2{caminho contato ≤ 2 arestas?}
  Path2 -->|sim| Allow2[INDIVIDUAL_INVITE_WITHIN_MAX_EDGES]
  Path2 -->|não| Bridge{entidade compartilhada autoriza?}
  Bridge -->|sim| Allow3[ENTITY_BRIDGE - sem teto de arestas]
  Bridge -->|não| Deny
  AllowE --> P2P[Handshake P2P + ledger C]
  Allow1 --> P2P
  Allow2 --> P2P
  Allow3 --> P2P
```

## 2. Mensagem P2P + ledger

```mermaid
sequenceDiagram
  autonumber
  participant UI as UI A
  participant Dom as App A domínio
  participant Net as Canal P2P
  participant DomB as App B domínio
  participant UIB as UI B

  UI->>Dom: enviar texto
  Dom->>Dom: can_open ainda válido?
  Dom->>Dom: AEAD + sign + append ledger
  Dom->>Net: ciphertext + seq + prev_hash
  Net->>DomB: entrega
  DomB->>DomB: verify + append ledger
  DomB->>UIB: atualiza projeção UI
```

## 3. Importar mídia da galeria e exportar com marca d’água

```mermaid
flowchart LR
  Gal[Galeria do SO] -->|copiar| Cofre[Cofre conversa C]
  Cofre -->|media_ref| Led[Ledger C]
  Cofre -->|export| WM[Marca d'água + metadados]
  WM -->|export_event| Led
  WM --> Fora[Arquivo fora do Ví]
```

## 4. Soft-delete / edição (UI only)

```mermaid
flowchart TD
  A[Usuário apaga/edita na UI] --> B[Atualiza projeção local]
  A --> C[append ui_hide_* ou message_correction]
  C --> D[Ledger intacto]
  B --> E[Lista/timeline sem o item]
  F[Recuperar conversa individual] --> G{K_A,C e K_B,C?}
  G -->|sim| H[Rematerializa UI a partir do ledger]
  G -->|não| I[Falha de recuperação]
```

## 5. Mudança de hardware

```mermaid
sequenceDiagram
  participant U as Usuário U
  participant Dev as Novo hardware
  participant Pol as HardwareRotationPolicy
  participant C1 as Conversa 1
  participant C2 as Conversa 2
  participant Cn as Conversa N

  U->>Dev: Ativa novo device
  Dev->>Pol: rotate_hardware(U, binding')
  Pol->>Pol: gerar K'_U,C para TODAS as conversas
  Pol->>C1: device_key_rotation
  Pol->>C2: device_key_rotation
  Pol->>Cn: device_key_rotation
  Note over Pol: Se tentar mudar chave só em C1 → NEGADO
```

## 6. Recuperação

```mermaid
flowchart TD
  subgraph Geral
    BG[Backup device root / identidade] --> RG[Restaura índice + envelopes]
    RG --> Nota1[Não exige todos os contatos online]
  end

  subgraph Individual
    RC[Pedido recuperar conversa C] --> Keys{Possui cooperação K_A,C e K_B,C?}
    Keys -->|sim| OK[Rematerializa ledger C na UI]
    Keys -->|não| Fail[Bloqueado]
  end
```
