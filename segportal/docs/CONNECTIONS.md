# Navegadores e pedidos de conexão — SegPortal TJSE

## Navegador HTML padrão (habilitado automaticamente)

Ao subir o SegPortal (`docker compose up` ou deploy K8s), o serviço **`web-browser`** (Firefox via VNC) sobe junto e o Job/serviço **`segportal-bootstrap`** cria a conexão **Navegador Web SegPortal** com permissão **READ para todos os usuários**.

Não é necessário seed manual.

- Protocolo: VNC → `web-browser:5900` (Firefox)
- Cliente: HTML5 no Guacamole (sem VPN/cliente)
- Sites internos e externos (externos via `proxy-egress` / IP TJSE quando configurado)

### Demo local

```bash
docker compose -f docker-compose.dev.yml up --build
# Aguarde o serviço segportal-bootstrap concluir (exit 0)
# http://localhost:8080/guacamole
# guacadmin / guacadmin  ou  usuario / usuario
# → abra "Navegador Web SegPortal"
```

Stack completo (com `.env`):

```bash
cp .env.example .env
docker compose up --build
```

Reaplicar bootstrap (idempotente):

```bash
./scripts/bootstrap-segportal.sh
```

---

## Pedidos de terminais/aplicações (com aprovação)

Usuários **não** criam conexões sozinhos. Fluxo:

```
Usuário solicita → status pending → Admin aprova/rejeita
       → se aprovado: conexão Guacamole + READ só para o solicitante
```

### Usuário solicita

```bash
./scripts/request-connection.sh usuario "RDP Financeiro 2" rdp 10.10.20.51 3389 \
  "Preciso do sistema de empenho no 2º semestre"
```

### Admin lista pendentes

```bash
psql ... -c "SELECT request_id, requester_username, connection_name, protocol, status
             FROM segportal_connection_request WHERE status='pending';"
```

### Admin aprova ou rejeita

```bash
./scripts/approve-connection-request.sh 1
./scripts/approve-connection-request.sh 1 --reject "Host fora da VLAN autorizada"
```

Política em `config/connections/requests.yaml`.

### Pela UI (Guacamole)

Enquanto a API/portal-auth não expõe formulário dedicado:

1. Usuário abre chamado / envia pedido (script ou futuro formulário)
2. Admin em **Settings → Connections** pode criar manualmente e conceder `READ` ao usuário
3. Ou usa os scripts acima (recomendado — registra auditoria na tabela `segportal_connection_request`)

---

## Arquitetura do navegador padrão

```
Usuário (HTML5)
    → Guacamole
        → guacd (VNC)
            → web-browser (Firefox)
                → sites internos
                → proxy-egress → internet (IP TJSE)
```

Componentes:

| Componente | Função |
|------------|--------|
| `services/web-browser` | Firefox em container com VNC (sobe no compose/K8s) |
| `scripts/bootstrap-segportal.sh` | Schema + conexão padrão + permissões (automático) |
| `guacd` | Protocolo VNC → stream HTML5 |
| `proxy-egress` | Saída controlada para externos |
| SQL `004-default-browser.sql` | Conexão + READ a todos os usuários |

No Kubernetes o Job `segportal-bootstrap` (`k8s/bootstrap`) aplica o mesmo bootstrap após o Postgres.

---

## Segurança

- Pedidos extras exigem justificativa e aprovação admin
- Navegador padrão é compartilhado como *conexão*; sessões Guacamole continuam individualizadas
- VNC sem senha **somente na rede interna** (não exponha a porta 5900)
- `SECURE_CONNECTION=0` no Firefox porque o Guacamole não usa VNC com TLS
- Ajuste a whitelist do Squid para limitar destinos externos

## Referências

- [ROLES.md](ROLES.md)
- [LOCAL_ADMIN.md](LOCAL_ADMIN.md)
- [CONFIGURATION.md](CONFIGURATION.md)
