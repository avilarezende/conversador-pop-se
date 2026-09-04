# Navegadores e pedidos de conexão — SegPortal TJSE

## Navegador HTML padrão (todos os usuários)

Todo usuário autenticado recebe, por padrão, a conexão **Navegador Web SegPortal**:

- Protocolo: VNC → pod `web-browser` (Firefox)
- Cliente: HTML5 no Guacamole (sem instalar navegador/VPN)
- Sites internos e externos (externos saem pelo `proxy-egress` com IP TJSE, quando configurado)

### Como habilitar (demo)

```bash
docker compose -f docker-compose.dev.yml up -d
# schema + papéis
docker compose -f docker-compose.dev.yml exec -T postgres \
  psql -U guacamole_user -d guacamole_db < scripts/sql/003-segportal-roles.sql
# navegador + pedidos
docker compose -f docker-compose.dev.yml exec -T postgres \
  psql -U guacamole_user -d guacamole_db < scripts/sql/004-default-browser.sql
docker compose -f docker-compose.dev.yml exec -T postgres \
  psql -U guacamole_user -d guacamole_db < scripts/sql/005-connection-requests.sql
```

Ou: `./scripts/seed-browser-and-requests.sh`

No portal, a conexão **Navegador Web SegPortal** aparece para admin e usuário.

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
| `services/web-browser` | Firefox em container com VNC |
| `guacd` | Protocolo VNC → stream HTML5 |
| `proxy-egress` | Saída controlada para externos |
| SQL `004-default-browser.sql` | Conexão + permissão a todos |

---

## Segurança

- Pedidos exigem justificativa e aprovação admin
- Navegador padrão é compartilhado como *conexão*; sessões continuam individualizadas no Guacamole
- Ajuste a whitelist do Squid para limitar destinos externos
- Não exponha a porta VNC do `web-browser` fora do cluster (só guacd acessa)

## Referências

- [ROLES.md](ROLES.md)
- [LOCAL_ADMIN.md](LOCAL_ADMIN.md)
- [CONFIGURATION.md](CONFIGURATION.md)
