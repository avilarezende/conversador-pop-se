# Criptografia pós-quântica e tempo real

## Objetivo

Proteger confidencialidade e autenticidade contra adversário clássico **e** adversário com computador quântico de larga escala, usando **somente criptografia de código aberto** e implementações auditáveis.

## Pilares (alvo)

| Uso | Família / algoritmo (NIST / open-source) | Papel |
|-----|------------------------------------------|-------|
| KEM (troca de chave) | **ML-KEM** (Kyber) via [liboqs](https://openquantumsafe.org/) / oqs-provider | Estabelecer segredo compartilhado |
| Assinatura | **ML-DSA** (Dilithium) via liboqs | Identidade, arestas, entradas do ledger |
| AEAD simétrica | **ChaCha20-Poly1305** ou **AES-256-GCM** | Payload do ledger e blobs |
| Hash | **SHA-3** / **BLAKE3** | Encadeamento do ledger, commitments |
| Híbrido (transição) | X25519 + ML-KEM | Defesa em profundidade até maturidade operacional PQC |

> Preferência: **modo híbrido** na fase inicial (clássico + PQC). Se um lado falhar por criptoanálise, o outro ainda protege.

## Stack open-source sugerida

- [Open Quantum Safe — liboqs](https://github.com/open-quantum-safe/liboqs)
- [oqs-provider](https://github.com/open-quantum-safe/oqs-provider) (OpenSSL 3)
- Binding Python: `oqspython` / ctypes sobre liboqs (adapter em `vinculo_crypto_pqc`)
- Mobile: bindings oficiais ou FFI a partir do cliente Flutter/Kotlin

O pacote `vinculo_crypto_pqc` **não** reimplementa PQC: apenas define **ports** e adapters para liboqs (e mocks determinísticos para testes).

## Modelo de ameaça (resumo)

| Ameaça | Mitigação |
|--------|-----------|
| Interceptação de mensagens em trânsito | E2EE com KEM PQC (+ híbrido) |
| Servidor curioso | Servidor vê metadados mínimos; sem plaintext |
| Adversário quântico futuro (“harvest now, decrypt later”) | KEM PQC desde o handshake |
| Personificação | Assinaturas ML-DSA em identidade e entradas |
| Manipulação de histórico | Hash-chain do ledger + assinaturas |
| Vazamento por exportação | Marca d’água + metadados + `export_event` |
| Clone de dispositivo | Épocas, revogação de device keys (fase 2) |

## Voz e vídeo

- Sinalização: canal de controle autenticado (mesma identidade PQC).
- Mídia: **WebRTC** (ou pipeline equivalente) com DTLS-SRTP; na evolução, integrar handshake com material PQC (hybrid) via inserter/adapter — o módulo `vinculo_realtime` isola esse detalhe.
- Gravação de chamada: se habilitada por política, vira entradas de mídia no **mesmo ledger** da conversa (nunca galeria “solta”).

## Gestão de chaves (conceitual)

```text
IdentityKeyPair_PQC     → longa duração, backup seguro
DeviceKeyPair_PQC       → por aparelho
ConversationEpochKey    → derivada via KEM entre participantes
MediaBlobKey            → por objeto, envelopada com epoch
```

Rotação: evento de domínio `EpochRotated` gera nova raiz; entradas antigas permanecem legíveis com épocas anteriores retidas localmente.

## Compliance de “código livre”

- Dependências criptográficas do núcleo: licenças OSI-approved (MIT/Apache/BSD).
- Proibido no núcleo: HSM/SDK proprietário opaco sem adapter opcional explícito fora do caminho crítico de testes.
- Documentar SBOMs das libs crypto em CI (fase de implementação).
