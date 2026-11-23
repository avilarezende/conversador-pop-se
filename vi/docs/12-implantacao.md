# Esquema de implantação — Ví

## Princípios

1. **Clientes** (mobile/web) detêm chaves de conversa e ledgers cifrados.
2. **Coordenação** é componente auxiliar (grafo, sinalização, discovery) — **sem plaintext**.
3. Código da aplicação Ví é **proprietário**; a documentação de conceito/lógica pode ser pública ([LICENCA-DOCUMENTACAO.md](LICENCA-DOCUMENTACAO.md)).
4. Bibliotecas cripto de terceiros (ex.: liboqs) entram como dependências com licenças próprias.

## Topologia alvo

```mermaid
flowchart TB
  subgraph Clients["Clientes"]
    M1[Mobile A]
    M2[Mobile B]
    W[Web entidade]
  end

  subgraph Edge["Borda"]
    LB[TLS terminator / API gateway]
  end

  subgraph Coord["Zona de coordenação"]
    API[vi-api composition root]
    PG[(Postgres metadados grafo)]
    SIG[Sinalização WebRTC]
  end

  subgraph Optional["Opcional - bytes opacos"]
    TURN[TURN relay]
    OBJ[(Object store cifrado - se usado)]
  end

  M1 <-->|P2P mídia/dados| M2
  M1 --> LB --> API
  M2 --> LB --> API
  W --> LB --> API
  API --> PG
  API --> SIG
  M1 -.-> TURN
  M2 -.-> TURN
  API -.-> OBJ
```

## Ambientes

| Ambiente | Papel |
|----------|-------|
| Dev local | `docker compose --profile vi` (API + Postgres + MinIO); crypto `mock` |
| Staging | Coordenação + clientes de teste; PQC híbrido |
| Produção | Clientes com keystore/HW binding; coordenação HA; sem logs de plaintext |

## O que NÃO implantar como “chat server” clássico

```mermaid
flowchart LR
  Bad[Servidor guarda mensagens em claro] -->|proibido| X[Fora do modelo Ví]
  Good[Servidor só metadados + sinalização] --> OK[Alinhado ao P2P]
```

## Separação código × documentação

```mermaid
flowchart TB
  subgraph Pub["Publicável"]
    D1[docs/ conceito e lógica]
    D2[Diagramas Mermaid]
    D3[LICENCA-DOCUMENTACAO]
  end

  subgraph Priv["Fechado / proprietário"]
    C1[packages/vi_*]
    C2[apps/api mobile web]
    C3[Secrets, builds, chaves]
  end

  Pub -.->|não inclui| Priv
```

## Diagrama de containers (esqueleto)

```mermaid
flowchart LR
  subgraph Host
    API[vi-api :8090]
    PG[(vi-postgres)]
    MINIO[(vi-minio)]
  end
  Dev[Desenvolvedor / testes] --> API
  API --> PG
  API --> MINIO
```

Perfil Compose: `vi` (ver `vi/docker-compose.yml`). Em produção o object store só recebe **blobs já cifrados** pelos clientes, se for usado.
