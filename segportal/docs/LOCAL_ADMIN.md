# Admin padrão e usuários locais — SegPortal AQNE

Manual operacional completo: **[ADMIN_MANUAL.md](ADMIN_MANUAL.md)**.  
Manual do usuário final: [USER_MANUAL.md](USER_MANUAL.md).

O SegPortal **sempre** possui autenticação local (PostgreSQL / JDBC), independente do LDAP. O administrador padrão é criado na inicialização do banco e permanece válido com LDAP ligado ou desligado.

O **portal-auth** (`:8090`) também autentica `guacadmin` / `usuario` em modo demo para o dashboard de arquivos.

---

## Admin padrão

| Campo | Valor inicial |
|-------|----------------|
| Usuário | `guacadmin` |
| Senha | `guacadmin` |
| Origem | Schema oficial Guacamole (`002-create-admin-user.sql`) |
| Depende de LDAP? | **Não** |

> **Obrigatório em produção:** altere a senha no primeiro acesso (ou via script abaixo) e restrinja quem conhece essa conta.

### Por que existe

- Bootstrap do portal sem AD disponível
- Conta de emergência se o LDAP/RADIUS falhar (`skip-if-unavailable: ldap`)
- Gestão de usuários locais e de apontamentos LDAP

---

## Alterar a senha do admin padrão

### Opção A — Interface Guacamole

1. Login como `guacadmin`
2. Menu do usuário → **Settings → Preferences** (ou perfil)
3. Defina a nova senha
4. Faça logout e valide o novo login

### Opção B — Script (SQL)

```bash
export POSTGRES_PASSWORD=...
./scripts/change-local-password.sh guacadmin 'NovaSenhaForte!'
```

Via Docker:

```bash
docker compose -f docker-compose.dev.yml exec -T postgres \
  env POSTGRES_PASSWORD=devpassword \
  bash -c 'apt-get update -qq && apt-get install -y -qq postgresql-client python3 >/dev/null'
# Ou rode o script a partir do host com psql apontando para a porta publicada
```

### Opção C — API REST Guacamole

Com token de sessão admin, `PUT /api/session/data/{dataSource}/users/guacadmin/password`.

---

## Desativar ou excluir o admin padrão

> Só faça isso **depois** de criar outro administrador local ou garantir admins via LDAP (`GG-SegPortal-Admin`).

### Desativar (recomendado)

Mantém o registro, impede login:

```bash
./scripts/delete-local-user.sh guacadmin --disable
```

### Excluir permanentemente

```bash
./scripts/delete-local-user.sh guacadmin --delete
```

Checklist antes de excluir:

1. Existe outro usuário com permissão `ADMINISTER`?
2. LDAP admin testado (se LDAP estiver habilitado)?
3. Backup do PostgreSQL realizado?

Para **reativar** um usuário desativado:

```sql
UPDATE guacamole_user u
SET disabled = FALSE
FROM guacamole_entity e
WHERE u.entity_id = e.entity_id AND e.name = 'guacadmin';
```

---

## Usuários locais (sem LDAP)

Com `LDAP_ENABLED=false` (padrão até o admin configurar o AD):

1. Login como `guacadmin`
2. **Settings → Users → New User**
3. Defina usuário, senha e permissões
4. Associe a grupos (`segportal-users`, `segportal-financeiro`, etc.) via `./scripts/seed-roles.sh` ou o bootstrap automático

O usuário demo `usuario` / `usuario` é criado pelo seed de papéis (opcional).

---

## Configurar apontamentos LDAP (pelo administrador)

Arquivo de referência: `config/ldap/ldap-settings.yaml`

| Campo | Variável / chave | Exemplo |
|-------|------------------|---------|
| Ligar LDAP | `LDAP_ENABLED` | `true` |
| Servidor | `LDAP_HOSTNAME` | `ldap.aqne.jus.br` |
| Porta | `LDAP_PORT` | `636` |
| Criptografia | `LDAP_ENCRYPTION_METHOD` | `ssl` / `starttls` / `none` |
| Domínio | `ldap.domain` | `aqne.jus.br` |
| Base DN | `LDAP_USER_BASE_DN` | `OU=Usuarios,DC=aqne,DC=jus,DC=br` |
| UID / atributo | `LDAP_USERNAME_ATTRIBUTE` | `sAMAccountName` ou `uid` |
| Bind DN | `LDAP_SEARCH_BIND_DN` | conta de serviço |
| Senha bind | `LDAP_SEARCH_BIND_PASSWORD` | Secret |
| Cadeia CA | `LDAP_CA_CHAIN_FILE` | PEM montado no pod |
| Cert. servidor | `LDAP_SERVER_CERTIFICATE_FILE` | opcional |

### Procedimento

1. Preencha `config/ldap/ldap-settings.yaml` (ou Secret/ConfigMap no Rancher)
2. Monte a cadeia CA em `/etc/guacamole/certs/ldap-ca-chain.pem`
3. Defina `LDAP_ENABLED=true` e demais variáveis
4. Reinicie o deployment `guacamole`
5. Teste login com conta AD **sem** remover o `guacadmin`

Se LDAP não for configurado (`LDAP_ENABLED=false`), o entrypoint remove todas as chaves `ldap-*` e o portal opera **somente com usuários locais**.

Detalhes técnicos: [CONFIGURATION.md](CONFIGURATION.md).

---

## Relação LDAP × usuários locais

```
LDAP_ENABLED=false  →  só JDBC (guacadmin + usuários locais)
LDAP_ENABLED=true   →  LDAP + JDBC (guacadmin continua válido)
LDAP fora do ar     →  skip-if-unavailable: ldap → login local permanece
```

---

## Referências

- [ROLES.md](ROLES.md) — papéis admin / usuário
- [CONFIGURATION.md](CONFIGURATION.md) — LDAP completo
- [SECURITY.md](SECURITY.md) — hardening
- Scripts: `change-local-password.sh`, `delete-local-user.sh`, `seed-roles.sh`, `bootstrap-segportal.sh`
