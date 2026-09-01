# Configuração — SegPortal TJSE

Referência de variáveis e arquivos de configuração.

## Variáveis de ambiente

Copie `.env.example` para `.env` no desenvolvimento local.

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `POSTGRES_DB` | Banco Guacamole | `guacamole_db` |
| `POSTGRES_USER` | Usuário PostgreSQL | `guacamole_user` |
| `POSTGRES_PASSWORD` | Senha PostgreSQL | *(obrigatório)* |
| `LDAP_HOSTNAME` | Servidor AD | `ldap.tjse.jus.br` |
| `LDAP_PORT` | Porta LDAPS | `636` |
| `LDAP_USER_BASE_DN` | Base de usuários | `OU=Usuarios,DC=tjse,DC=jus,DC=br` |
| `LDAP_SEARCH_BIND_DN` | Conta de serviço | `CN=svc-segportal,...` |
| `LDAP_SEARCH_BIND_PASSWORD` | Senha da conta de serviço | *(obrigatório)* |
| `MFA_ENABLED` | Habilitar RADIUS MFA | `true` |
| `MFA_RADIUS_HOST` | Servidor RADIUS | `radius.tjse.jus.br` |
| `MFA_RADIUS_SECRET` | Shared secret RADIUS | *(obrigatório)* |
| `SESSION_TIMEOUT_MINUTES` | Timeout de inatividade | `60` |
| `EGRESS_PROXY_HOST` | Host do Squid | `proxy-egress` |
| `GUACAMOLE_HOSTNAME` | Hostname público | `segportal.tjse.jus.br` |

## Arquivos de configuração

### `config/guacamole/guacamole.properties`

Template renderizado pelo `entrypoint.sh` com `envsubst`. Define backend PostgreSQL, LDAP, RADIUS e proxy HTTP.

### `config/ldap/ldap.properties`

Referência de mapeamento AD → grupos SegPortal. Grupos exemplo:

| Grupo AD | Recursos |
|----------|----------|
| `GG-SegPortal-Financeiro` | RDP estações financeiro |
| `GG-SegPortal-Consulta` | VNC terminais processuais |
| `GG-SegPortal-Admin` | SSH + proxy egress |

### `config/proxy/squid.conf`

Whitelist de domínios para egress HTTP (`.tjse.jus.br`, `.jus.br`, `.gov.br`, `.pje.jus.br`).

## Imagem Guacamole

O `Dockerfile` em `services/guacamole/`:

- Base: `guacamole/guacamole:1.5.5`
- Extensão: `guacamole-auth-ldap-1.5.5.jar`
- Build context: **raiz do repositório**

## Kubernetes

Secrets (não commitar valores reais):

- `k8s/postgres/secret.example.yaml`
- `k8s/guacamole/secret.example.yaml`

ConfigMap comum: `k8s/base/configmap-common.yaml`

Overlays ajustam hostname e réplicas:

- `k8s/overlays/development`
- `k8s/overlays/staging`
- `k8s/overlays/production`

## Inicialização do banco

```bash
export POSTGRES_PASSWORD=...
./scripts/init-db.sh
```

Aplica schema oficial Guacamole 1.5.5 para PostgreSQL.

## Branding TJSE

Arquivos em `services/guacamole/branding/`:

- `tjse-logo.svg` — logotipo no login
- `guac-login.css` — cores institucionais (#003366, #c9a227)
- `translations/pt.json` — strings em português
