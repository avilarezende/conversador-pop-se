# Diagrama de classes — domínio Ví

Visão lógica (conceito). Nomes alinhados aos pacotes `vi_*`; a implementação proprietária pode variar, mantendo os contratos.

## Visão geral dos contextos

```mermaid
classDiagram
  direction LR

  class NodeId
  class ConversationId
  class NodeKind {
    <<enumeration>>
    INDIVIDUAL
    ENTITY
  }

  class IdentityRecord {
    node_id
    kind
    display_name
    pqc_sign_public_key
    pqc_kem_public_key
  }

  class DeviceRecord {
    device_id
    node_id
    hardware_binding
  }

  class Edge {
    src
    dst
    edge_type
    anchor_id
    pair_with
  }

  class TrustPolicy {
    max_path_edges
    decide()
  }

  class Decision {
    allowed
    reason
    entity
    path
  }

  class LedgerEntry {
    conversation_id
    seq
    prev_hash
    entry_hash
    entry_type
    payload_ciphertext
    sender_id
  }

  class ConversationKey {
    user_id
    conversation_id
    hardware_binding
    key_material
  }

  class MediaBlob {
    blob_id
    conversation_id
    creator_id
    ciphertext
  }

  IdentityRecord --> NodeId
  IdentityRecord --> NodeKind
  DeviceRecord --> NodeId
  Edge --> NodeId
  TrustPolicy --> Decision
  LedgerEntry --> ConversationId
  ConversationKey --> ConversationId
  MediaBlob --> ConversationId
```

## Ports (contratos hexagonais)

```mermaid
classDiagram
  direction TB

  class TrustGraphPort {
    <<protocol>>
    add_edge(edge)
    add_anchor(anchor)
    can_open_channel(a, b, at) Decision
  }

  class ConversationLedgerPort {
    <<protocol>>
    ensure_conversation(id)
    append(...) LedgerEntry
    verify_chain(id) bool
    list_entries(id)
  }

  class MediaExportPort {
    <<protocol>>
    store(blob)
    export_with_watermark(blob_id, exporter) ExportedMedia
  }

  class PqcCryptoPort {
    <<protocol>>
    generate_kem_keypair()
    generate_sign_keypair()
    kem_encapsulate(pk)
    kem_decapsulate(sk, ct)
    sign(sk, msg)
    verify(pk, msg, sig)
    aead_encrypt(key, pt)
    aead_decrypt(key, ct)
  }

  class ConversationKeyPort {
    <<protocol>>
    get(user, conversation)
    rotate_hardware(user, new_binding, all_conversation_ids)
    assert_not_partial_rotation(...)
  }

  class RealtimeSessionPort {
    <<protocol>>
    start_session(conversation, initiator, peer)
    end_session(session_id)
  }

  class InMemoryTrustGraph
  class InMemoryLedger
  class MediaIntegrityService
  class MockPqcProvider

  TrustGraphPort <|.. InMemoryTrustGraph
  ConversationLedgerPort <|.. InMemoryLedger
  MediaExportPort <|.. MediaIntegrityService
  PqcCryptoPort <|.. MockPqcProvider
```

## Tipos de entrada do ledger

```mermaid
classDiagram
  class EntryType {
    <<enumeration>>
    MESSAGE
    MEDIA_REF
    AV_SESSION
    POLICY
    EXPORT_EVENT
    MESSAGE_CORRECTION
    UI_HIDE_ENTRY
    UI_HIDE_CONVERSATION
    DEVICE_KEY_ROTATION
  }
```

## Regras de chave (resumo em classes)

```mermaid
classDiagram
  class HardwareRotationPolicy {
    rotate(user, new_binding, conversations)
    reject_partial_change(user, single_conversation)
  }

  class RecoveryPolicy {
    recover_account(device_root)
    recover_conversation(A, B, C) 
  }

  note for RecoveryPolicy "Recuperação geral NÃO exige todos os contatos.\nRecuperação individual de C exige K_A,C e K_B,C."
  note for HardwareRotationPolicy "Mudança só em uma conversa → PARTIAL_KEY_ROTATION_FORBIDDEN.\nHW novo → notificar TODAS as conversas."
```
