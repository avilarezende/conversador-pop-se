# Ledger de conversa e integridade de mídia

## Ideia central

Cada canal autorizado possui um **ledger append-only** próprio: uma cadeia de blocos/entradas criptografadas que registra mensagens, anexos e eventos de sessão (entrada, revogação, exportação). O ledger **não** é uma blockchain pública global; é um **diário criptografado por conversa**, no espírito de hash-chain / accountability log.

## Por que separar cofres

| Cofre | Conteúdo | Acesso |
|-------|----------|--------|
| **Galeria do aparelho** | Fotos/vídeos do SO | App pode *buscar* para anexar |
| **Ledger da conversa** | Ciphertext + hashes + refs de mídia interna | Só participantes + chaves da conversa |
| **Blob store criptografado** | Bytes de mídia interna | Chave derivada do ledger / epoch |

Mídia importada da galeria, ao entrar no Ví, é **copiada para o cofre da conversa** (recriptografada). A original no aparelho não faz parte do ledger.

## Estrutura de uma entrada do ledger

```text
LedgerEntry {
  conversation_id
  seq                  # monotônico
  prev_hash            # hash da entrada anterior
  entry_type           # message | media_ref | av_session | policy | export_event
  payload_ciphertext   # AEAD (chave de época da conversa)
  content_hash         # hash do plaintext lógico (compromisso)
  sender_id
  sender_sig_pqc       # assinatura pós-quântica do remetente
  created_at
}
```

Propriedades:

- **Append-only:** não há “editar mensagem” silenciosa; correção = nova entrada que aponta a anterior.
- **Encadeamento:** alteração de histórico quebra `prev_hash`.
- **Criptografia em descanso:** payload ilegível sem chaves da conversa.
- **Isolamento:** chaves e blobs de conversa C1 não abrem C2.

## Épocas de chave

Chaves de conversa rotacionam por **época** (tempo, número de mensagens, ou evento de segurança). Cada época deriva:

- `k_msg` — AEAD de texto
- `k_media` — envelopamento de blobs
- `k_export` — material ligado à marca d’água / binding (não é a chave de leitura)

## Mídia

### Importar do aparelho

1. Usuário seleciona arquivo na galeria (permissionamento do SO).
2. App calcula hash, extrai metadados mínimos, gera blob criptografado no cofre.
3. Ledger recebe `media_ref` (hash, tipo, tamanho, epoch, sender).

### Exportar mídia interna

Toda exportação **obrigatoriamente**:

1. Aplica **marca d’água visual** (imagem/vídeo) e/ou fingerprint perceptivo com:
   - identificador do **responsável pela exportação** (quem exportou);
   - identificador agregado do **criador** da mídia no ledger;
   - `conversation_id` truncado / commitment;
   - timestamp da exportação.
2. Injeta **metadados** (EXIF/XMP/container) com o mesmo vínculo e assinatura.
3. Registra `export_event` no ledger (auditoria).

> Mídia exportada **não** é uma cópia “limpa” do cofre. Sem marca d’água + metadados, o fluxo de exportação falha fechado.

## Busca

- Busca na **galeria do SO**: via APIs nativas; resultados não entram no ledger até anexados.
- Busca **dentro do Ví**: sobre metadados/index local descriptografado no dispositivo do participante (nunca plaintext no servidor de coordenação, no desenho alvo).

## Sincronização e multi-dispositivo

Fase 1 do esqueleto: **um dispositivo primário** + backup criptografado do ledger.
Fase posterior: multi-device com re-envelope de épocas (módulo `ledger` + `identity`).
