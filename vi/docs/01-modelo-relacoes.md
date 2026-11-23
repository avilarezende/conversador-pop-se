# Modelo de relações — grafo de confiança

## Vocabulário

| Termo | Definição |
|-------|-----------|
| **Nó indivíduo** | Pessoa com identidade e chaves no Ví |
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

### Escopo do limite de arestas

| Par | Limite `max_path_edges` (padrão: 2) |
|-----|-------------------------------------|
| **Indivíduo ↔ indivíduo** (convite / canal via `contato_direto`) | **Sim** — no máximo 2 arestas no caminho |
| **Entidade reconhecida** (contato com indivíduo ou ponte `autoriza_par` / membros) | **Não** — a restrição de arestas **não se aplica** |

### R1 — Contato direto (1º grau)

Existe aresta mútua `contato_direto` entre `A` e `B`.

### R1b — Convite indivíduo–indivíduo (≤ 2 arestas)

`A` e `B` são indivíduos e existe caminho de `contato_direto` **mútuo** com **no máximo 2 arestas** (ex.: amigo do amigo: `A→B→C`).

Caminhos com 3 ou mais arestas só de indivíduos **não** abrem canal por esta regra.

### R2 — Entidade contacta indivíduo

Uma **entidade reconhecida** `E` pode abrir canal com `A` se `A` **reconhece** `E` (ou `A` é `membro_de` `E` conforme política).

Sem limite de distância no grafo de indivíduos: a restrição de arestas não vale para entidades.

### R3 — Ponte por entidade (sem teto de arestas)

`A` e `B` (indivíduos) podem conversar se existe entidade `E` tal que:

1. `A` reconhece `E` **e** `B` reconhece `E`; **e**
2. `E` emite `autoriza_par(A, B)` (explícito) **ou** ambos são `membro_de E` sob política que permita peer-to-peer intramembro.

A entidade pode autorizar o par mesmo quando `A` e `B` estariam além de 2 arestas no grafo de contatos pessoais.

### R4 — Âncora de local/evento

Quando a política do módulo exigir:

- A aresta ou a autorização `autoriza_par` deve referenciar uma **âncora** válida (janela temporal + geofence opcional + assinatura da entidade).
- Expirada a âncora, novas mensagens podem ser bloqueadas; o ledger histórico permanece.

## Pseudocódigo da decisão

```text
function can_open_channel(A, B, graph, now):
  if A == B: return deny

  # Entidade: sem limite de arestas
  if is_entity(B) and A.recognizes(B):
    return allow(reason=ENTITY_TO_INDIVIDUAL)
  if is_entity(A) and B.recognizes(A):
    return allow(reason=ENTITY_TO_INDIVIDUAL)

  if both_individuals(A, B):
    if graph.has_mutual_direct_contact(A, B):
      return allow(reason=DIRECT_1ST_DEGREE)

    path = shortest_mutual_contact_path(A, B)   # só indivíduos
    if path is not None and path.edge_count <= max_path_edges:  # default 2
      return allow(reason=INDIVIDUAL_INVITE_WITHIN_MAX_EDGES, path=path)

    for E in graph.recognized_entities_shared_by(A, B):
      if E.permits_pair(A, B, now):
        if policy.requires_anchor and not E.pair_anchor_valid(A, B, now):
          continue
        return allow(reason=ENTITY_BRIDGE, entity=E)  # sem teto de arestas

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
