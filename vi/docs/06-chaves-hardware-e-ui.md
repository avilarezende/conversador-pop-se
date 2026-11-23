# Chaves por conversa, hardware e efeitos só de UI

## Apagar / editar na interface ≠ apagar no ledger

Usuários **podem** apagar conversas ou editar mensagens na UI. O efeito é **somente na projeção gráfica** (lista, timeline filtrada, “não mostrar”).

No ledger:

- o material **continua existindo**;
- a ação gera **registros append-only** (`ui_hide_conversation`, `ui_hide_entry`, `message_correction` apontando à entrada original);
- não há rewrite silencioso da cadeia.

Recuperar o histórico “apagado” na UI = voltar a materializar entradas que já estão no ledger (sujeito às chaves abaixo).

## Chave por conversa, vinculada ao hardware

Cada usuário `U` possui, para cada conversa `C` em que participa, uma **chave de conversa** `K_{U,C}`:

```text
K_{U,C}  ←  derivada / envelopada com material do dispositivo (hardware binding)
HardwareBinding = f(device_attestation | secure_enclave_id | install_id estável)
```

Propriedades:

| Propriedade | Regra |
|-------------|--------|
| Escopo | Uma chave **por usuário por conversa** |
| Binding | Ligada ao **hardware** atual do usuário |
| Isolamento | `K_{U,C1}` não abre `C2` |
| Troca de aparelho | Gera **nova** família de chaves e **notifica todas** as conversas |

O ciphertext do ledger de `C` só é legível com cooperação das chaves dos participantes (para 1:1: ambos os indivíduos).

## Recuperação

| Cenário | Depende de |
|---------|------------|
| **Recuperação individual** do ledger de uma conversa (ex.: UI “apagada”, novo client quer rematerializar `C`) | Chaves dos **dois** indivíduos da conversa (`K_{A,C}` e `K_{B,C}` na época vigente) |
| **Recuperação geral** da conta / dispositivo (backup de identidade + device root) | **Não** depende de ter todos os contatos online; restaura o envelope de dispositivo e o índice de conversas |

Ou seja: backup geral ≠ reabrir cada conversa; reabrir cada conversa “escondida” exige o par de chaves daquela conversa.

## Mudança de hardware (obrigatória e global)

Quando o hardware muda (novo aparelho, reinstall com novo binding, rotação forçada):

1. Gera-se novo `HardwareBinding` e novas `K'_{U,C}` para **todas** as conversas de `U`.
2. Emite-se `device_key_rotation` (ou equivalente) **em todas** as conversas ativas de `U`, com commitment da nova chave pública de conversa / epoch.
3. Contatos atualizam o envelope da época; épocas antigas ficam retidas para ler histórico, conforme política.

### Proibição de rotação parcial

Se for detectada mudança de chave **apenas em uma conversa** (sem o evento global de hardware / sem notificação às demais):

- a operação é **negada** (`PARTIAL_KEY_ROTATION_FORBIDDEN`);
- o peer pode tratar como anomalia de integridade (alerta, congelar appends até resolver).

```text
allowed = rotation.is_hardware_global
       AND notified_conversation_ids == all_conversations_of(U)
       AND binding_changed == true
```

## Tipos de entrada no ledger (complemento)

| `entry_type` | Significado |
|--------------|-------------|
| `message_correction` | “Edição” de UI: nova entrada referencia `seq` anterior; plaintext antigo permanece cifrado na entrada original |
| `ui_hide_entry` | Ocultar mensagem na UI do autor (ou acordo local); ledger intacto |
| `ui_hide_conversation` | Ocultar conversa na UI do autor; ledger intacto |
| `device_key_rotation` | Aviso de nova chave de conversa por mudança de hardware (deve aparecer em **todas** as conversas do usuário) |

## Relação com épocas (doc 03)

- `K_{U,C}` alimenta a derivação de `ConversationEpochKey` junto ao peer.
- Rotação de hardware ⇒ nova época em cada conversa + registros `device_key_rotation`.
- Soft-delete de UI **não** rotaciona chave e **não** apaga épocas.
