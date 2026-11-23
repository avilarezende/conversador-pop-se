# Arquitetura — padrão e módulos

## Decisão de padrão

### Escolhido: **Monólito Modular + Hexagonal (Ports & Adapters) + Bounded Contexts**

Também conhecido na prática como *modular monolith* com *clean/hexagonal boundaries*.

```
                    ┌─────────────────────────────────────┐
                    │         Apps (api / mobile / web)   │
                    │         composition root            │
                    └─────────────────┬───────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          │                           │                           │
   ┌──────▼──────┐             ┌──────▼──────┐             ┌──────▼──────┐
   │ trust_graph │             │   ledger    │             │   media     │
   │  (domínio)  │             │  (domínio)  │             │  (domínio)  │
   └──────┬──────┘             └──────┬──────┘             └──────┬──────┘
          │ ports                     │ ports                     │ ports
   ┌──────▼──────┐             ┌──────▼──────┐             ┌──────▼──────┐
   │ adapters:   │             │ adapters:   │             │ adapters:   │
   │ graph store │             │ chain store │             │ watermark   │
   │ policy eng. │             │ blob store  │             │ gallery FS  │
   └─────────────┘             └─────────────┘             └─────────────┘

   identity · crypto_pqc · realtime  (mesma forma)
```

### Por que não (ainda) microsserviços

| Alternativa | Motivo de adiamento |
|-------------|---------------------|
| Microsserviços por domínio | Latência e consistência do grafo+ledger no caminho crítico; ops prematura |
| Plugin runtime dinâmico só | Útil depois; primeiro precisamos de contratos estáveis em pacotes |
| Clean Architecture “em camadas globais” sem módulos | Vira um monólito rígido; features novas misturam regras |

### Por que este padrão encaixa o produto

1. **Grafo, ledger, mídia, A/V e crypto** são contextos com linguagens e ciclos de vida diferentes.
2. Novas features (ex.: credenciais verificáveis, geofence, compliance LGPD) = **novo pacote + adapters**, sem reabrir o núcleo.
3. Testes de domínio sem banco/rede (ports mockados).
4. Extração futura: um pacote vira serviço mantendo as mesmas interfaces.

## Bounded contexts (pacotes)

| Pacote | Responsabilidade | Não faz |
|--------|------------------|---------|
| `vinculo_core` | IDs, erros, eventos base, clock | Regras de negócio específicas |
| `vinculo_identity` | Perfis, device keys, reconhecimento | Decidir se canal pode abrir |
| `vinculo_trust_graph` | Arestas, âncoras, `can_open_channel` | Armazenar mensagens |
| `vinculo_ledger` | Hash-chain, épocas, append | Watermark visual |
| `vinculo_media` | Import/export, marca d’água, metadados | Política de grafo |
| `vinculo_realtime` | Sessões voz/vídeo, sinalização | Persistência de chat |
| `vinculo_crypto_pqc` | KEM, sign, AEAD via liboqs | UX |

Comunicação **entre** contextos: eventos de domínio / application services na API — **não** imports cruzados profundos de infraestrutura.

## Ports principais (exemplos)

```python
class TrustGraphPort(Protocol):
    def can_open_channel(self, a: NodeId, b: NodeId, at: datetime) -> Decision: ...
    def add_edge(self, edge: Edge) -> None: ...

class ConversationLedgerPort(Protocol):
    def append(self, conversation_id: str, entry: LedgerEntryDraft) -> LedgerEntry: ...
    def verify_chain(self, conversation_id: str) -> bool: ...

class MediaExportPort(Protocol):
    def export_with_watermark(self, blob_id: str, exporter: NodeId) -> ExportedMedia: ...

class PqcCryptoPort(Protocol):
    def kem_encapsulate(self, public_key: bytes) -> tuple[bytes, bytes]: ...
    def sign(self, private_key: bytes, message: bytes) -> bytes: ...
```

## Apps

- **`apps/api`** — composition root FastAPI: wiring de adapters, rotas finas, feature flags.
- **`apps/mobile`** — esqueleto Flutter (Dart): telas stub + contratos de plugin crypto/media.
- **`apps/web`** — esqueleto estático/TS mínimo para painel de entidade (fase posterior).

## Configuração modular

`config/modules.yaml` liga/desliga capacidades:

```yaml
modules:
  trust_graph: { enabled: true }
  ledger: { enabled: true }
  media_watermark: { enabled: true }
  realtime_av: { enabled: false }      # feature flag
  crypto_pqc:
    enabled: true
    hybrid: true
    provider: mock   # mock | liboqs
```

## Diagrama de fluxo — abrir conversa e enviar mídia

```text
Cliente                API                 trust_graph          ledger           media
  │  open(A,B)          │                     │                  │               │
  │────────────────────►│ can_open?            │                  │               │
  │                     │────────────────────►│                  │               │
  │                     │◄──── allow/deny ────│                  │               │
  │                     │ create/ensure conv  │                  │               │
  │                     │───────────────────────────────────────►│               │
  │  attach gallery     │                     │                  │               │
  │────────────────────►│ import              │                  │               │
  │                     │───────────────────────────────────────────────────────►│
  │                     │ append media_ref    │                  │◄──────────────│
  │                     │───────────────────────────────────────►│               │
  │  export             │                     │                  │               │
  │────────────────────►│ export_with_wm      │                  │               │
  │                     │───────────────────────────────────────────────────────►│
  │                     │ append export_event │                  │◄──────────────│
  │                     │───────────────────────────────────────►│               │
```

## Stack sugerida (esqueleto)

| Camada | Tecnologia |
|--------|------------|
| Domínio / API | Python 3.12+, FastAPI |
| Pacotes | namespace `vinculo_*` instaláveis em editable |
| Persistência (dev) | Postgres (metadados) + filesystem/MinIO (blobs) |
| Crypto | adapter `mock` agora; `liboqs` na implementação |
| Mobile | Flutter (iOS/Android) |
| Tempo real | WebRTC (flag desligada no esqueleto) |

Python foi escolhido no esqueleto para alinhar ao monorepo atual e prototipar regras de grafo/ledger com testes rápidos. O padrão hexagonal **permite** reescrever adapters em Rust/Go depois sem mudar os ports.
