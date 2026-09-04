# Papéis de acesso — SegPortal TJSE

O SegPortal usa **dois papéis principais**, alinhados a grupos do Active Directory e a grupos internos do Guacamole.

![Mockup com papéis](images/segportal-mockup.jpg)

---

## Resumo

| Papel | Grupo AD | Grupo Guacamole | Escopo |
|-------|----------|-----------------|--------|
| **Administrador** | `GG-SegPortal-Admin` | `segportal-admins` | Portal inteiro |
| **Usuário** | `GG-SegPortal-Usuarios` | `segportal-users` | Apenas o próprio contexto |

Grupos de negócio (Financeiro, Consulta, Externo) limitam **quais conexões** o usuário vê. O papel **admin** enxerga e configura tudo; o **usuário** só conecta ao que foi liberado ao seu grupo.

---

## Administrador

### Pode

- Visualizar **sessões ativas** de qualquer usuário (monitoramento / auditoria)
- Criar, editar e remover **conexões** (RDP, VNC, SSH, bookmarks)
- Gerenciar **usuários e grupos** no Guacamole
- Associar conexões a grupos de clientes
- Consultar histórico e eventos de auditoria (`ADMINISTER`)

### Permissões Guacamole (sistema)

```
ADMINISTER
CREATE_CONNECTION
CREATE_CONNECTION_GROUP
CREATE_SHARING_PROFILE
CREATE_USER
CREATE_USER_GROUP
```

### Contas

| Ambiente | Login | Observação |
|----------|-------|------------|
| Produção (LDAP) | Conta AD membro de `GG-SegPortal-Admin` | MFA obrigatório |
| Demo local | `guacadmin` / `guacadmin` | Alterar senha após primeiro acesso |

---

## Usuário normal

### Pode

- Ver **somente** as conexões liberadas aos seus grupos de negócio
- Abrir sessões RDP/VNC/SSH/proxy no **próprio** contexto
- Encerrar a **própria** sessão

### Não pode

- Ver sessões de outros usuários
- Configurar conexões, usuários ou grupos
- Acessar Settings administrativos do Guacamole
- Expandir o próprio perfil além do que o AD concedeu

### Permissões Guacamole

- **Sistema:** nenhuma
- **Conexões:** apenas `READ` nas conexões dos grupos de negócio

### Contas

| Ambiente | Login | Observação |
|----------|-------|------------|
| Produção (LDAP) | Conta AD em `GG-SegPortal-Usuarios` + grupo de negócio | MFA obrigatório |
| Demo local | `usuario` / `usuario` | Grupo `segportal-financeiro` |

---

## Isolamento de sessão (premissa de segurança)

```
Admin ──► vê / audita sessões de todos (`ADMINISTER`)
Usuário ──► vê apenas a própria sessão ativa
```

Cada sessão Guacamole permanece **individualizada** (connection ID + username). O papel usuário **não** recebe `ADMINISTER`, o que impede listar sessões alheias.

---

## Como aplicar (demo local)

```bash
# Após docker compose -f docker-compose.dev.yml up
export POSTGRES_PASSWORD=devpassword
# Se postgres estiver só no Docker:
docker compose -f docker-compose.dev.yml exec -T postgres \
  psql -U guacamole_user -d guacamole_db < scripts/sql/003-segportal-roles.sql

# Ou com psql local:
./scripts/seed-roles.sh
```

## Produção (LDAP)

1. Criar no AD: `GG-SegPortal-Admin` e `GG-SegPortal-Usuarios`
2. Criar grupos de negócio (`GG-SegPortal-Financeiro`, etc.)
3. No Guacamole, criar user groups com **os mesmos nomes** dos grupos AD
4. Conceder permissões de sistema ao grupo admin (conforme tabela acima)
5. Associar conexões apenas aos grupos de negócio (READ)

Referência completa: [CONFIGURATION.md](CONFIGURATION.md) e `config/roles/roles.yaml`.

---

## Matriz rápida

| Capacidade | Admin | Usuário |
|------------|:-----:|:-------:|
| Login LDAP + MFA | ✓ | ✓ |
| Conectar aos próprios recursos | ✓ | ✓ |
| Ver sessões de terceiros | ✓ | ✗ |
| Configurar aplicações/conexões | ✓ | ✗ |
| Gerenciar usuários/grupos | ✓ | ✗ |
| Auditoria / histórico global | ✓ | ✗ |
