# Modelo de relações — grafo de confiança

## Vocabulário

| Termo | Definição |
|-------|-----------|
| **Nó indivíduo** | Pessoa com identidade e chaves no Vínculo |
| **Nó entidade** | Organização/instituição *reconhecida* (status verificado por política) |
| **Âncora** | Local ou evento real ao qual uma aresta ou autorização pode estar ligada |
| **Aresta** | Relação dirigida ou mútua: `reconhece`, `contato_direto`, `membro_de`, `autoriza_par` |
| **Grau** | Distância em arestas no grafo de relações |
| **Canal** | Sessão de mensagens entre dois nós, só criada se a política permitir |

## Tipos de aresta (v1 conceitual)

```
individuo --reconhece--> entidade
entidade  --reconhece--> individuo   (opcional; ou implícito via membership)
individuo --contato_direto--> individuo   (1º grau, mútuo)
individuo --membro_de--> entidade
entidade  --autoriza_par--> (individuo_A, individuo_B)  [com âncora opcional]
aresta.*  --ancorada_em--> local_ou_evento
```

## Regras de contato (política v0)

Seja `A` e `B` indivíduos. Um canal `A ↔ B` é permitido se **qualquer** condição for verdadeira:

### R1 — Contato direto (1º grau)

Existe aresta mútua `contato_direto` entre `A` e `B`.

### R2 — Entidade contacta indivíduo

Uma **entidade reconhecida** `E` pode abrir canal com `A` se `A` **reconhece** `E` (ou `A` é `membro_de` `E` conforme política).

### R3 — Ponte por entidade (máx. 2 saltos)

`A` e `B` podem conversar se existe entidade `E` tal que:

1. `A` reconhece `E` **e** `B` reconhece `E`; **e**
2. `E` emite `autoriza_par(A, B)` (explícito) **ou** ambos são `membro_de E` sob política que permita peer-to-peer intramembro; **e**
3. O caminho efetivo no grafo tem **no máximo 2 arestas** entre `A` e `B` passando por `E` (ex.: `A→E→B`).

> **Hard limit:** pesquisa / autorização de canal **não** desce além de **2 níveis de arestas**. Não há “amigo do amigo do amigo”.

### R4 — Âncora de local/evento

Quando a política do módulo exigir:

- A aresta ou a autorização `autoriza_par` deve referenciar uma **âncora** válida (janela temporal + geofence opcional + assinatura da entidade).
- Expirada a âncora, novas mensagens podem ser bloqueadas; o ledger histórico permanece.

## Pseudocódigo da decisão

```text
function can_open_channel(A, B, graph, now):
  if A == B: return deny

  if graph.has_mutual_direct_contact(A, B):
    return allow(reason=DIRECT_1ST_DEGREE)

  for E in graph.recognized_entities_shared_by(A, B):
    path = shortest_path(A, B, via=E, edge_types=ALLOWED)
    if path.length <= 2 and E.permits_pair(A, B, now):
      if policy.requires_anchor and not path.anchor_valid(now):
        continue
      return allow(reason=ENTITY_BRIDGE, entity=E, path=path)

  # Entidade como endpoint (não par indivíduo-indivíduo)
  if is_entity(B) and A.recognizes(B):
    return allow(reason=ENTITY_TO_INDIVIDUAL)

  return deny(reason=NO_VALID_PATH)
```

## Associação a local/evento

```yaml
anchor:
  id: evt_workshop_ifs_2026
  kind: event            # event | place
  label: "Workshop Segurança IFS"
  place: { lat, lon, radius_m }   # opcional
  valid_from: 2026-11-12T08:00:00-03:00
  valid_until: 2026-11-14T22:00:00-03:00
  issued_by: entidade:ifs
  signature: ...         # assinatura PQC da entidade
```

A âncora **não substitui** a regra de grafo; ela **restringe** o escopo temporal/espacial da autorização.

## Estados de relação

- `pending` — convite/QR aguardando aceite
- `active` — aresta válida
- `revoked` — removida por um dos lados ou pela entidade
- `expired` — âncora ou TTL esgotado

Revogação **não apaga** o ledger; apenas impede novos appends e novas sessões A/V.

## Privacidade do grafo

- O servidor de coordenação pode armazenar **metadados de arestas** necessários à política (com minimização).
- Provas de caminho podem evoluir para **credenciais verificáveis / ZK** em fase posterior (módulo `trust_graph` preparado para trocar o adapter).
