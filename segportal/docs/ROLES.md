# Papéis de acesso — SegPortal TJSE

O SegPortal usa **dois papéis principais**, alinhados a grupos do Active Directory e a grupos internos do Guacamole.

![Mockup com papéis](images/segportal-mockup.jpg)

---

## Resumo

| Papel | Grupo AD | Grupo Guacamole | Escopo |
|-------|----------|-----------------|--------|
| **Administrador** | `GG-SegPortal-Admin` | `segportal-admins` | Portal inteiro |
| **Usuário** | `GG-SegPortal-Usuarios` | `segportal-users` | Apenas o próprio contexto |

**Todos** os papéis recebem o **Navegador Web SegPortal** automaticamente no boot.

Grupos de negócio (Financeiro, Consulta, Externo) limitam **quais conexões extras** o usuário vê. O **admin** enxerga e configura tudo; o **usuário** só conecta ao liberado (navegador padrão + aprovados).

Fonte: `config/roles/roles.yaml`.

---

## Administrador

### Pode

- Visualizar **sessões ativas** de qualquer usuário
- Criar, editar e remover **conexões** (RDP, VNC, SSH, browser)
- **Aprovar / rejeitar** pedidos de terminais e aplicações
- Gerenciar **usuários e grupos** no Guacamole
- Configurar **apontamentos LDAP** (quando aplicável)
- Consultar auditoria (`ADMINISTER`)

![Painel administrativo](images/admin-approvals.jpg)

### Contas

| Ambiente | Login | Observação |
|----------|-------|------------|
| Qualquer (local) | `guacadmin` / `guacadmin` | **Independente do LDAP** — alterar senha no 1º acesso |
| Produção (LDAP) | Conta AD em `GG-SegPortal-Admin` | MFA se habilitado |

Ver [LOCAL_ADMIN.md](LOCAL_ADMIN.md).

---

## Usuário normal

### Pode

- Usar o **Navegador Web SegPortal** (padrão automático)
- Ver conexões liberadas aos seus grupos de negócio
- **Solicitar** novos terminais/aplicações (sujeito a aprovação)
- Abrir sessões no **próprio** contexto
- Encerrar a **própria** sessão

### Não pode

- Ver sessões de outros usuários
- Criar conexões sem aprovação
- Acessar Settings administrativos
- Expandir o próprio perfil além do AD/admin

### Contas

| Ambiente | Login | Observação |
|----------|-------|------------|
| Produção (LDAP) | Conta em `GG-SegPortal-Usuarios` + grupo de negócio | MFA se habilitado |
| Demo local | `usuario` / `usuario` | Após bootstrap |

---

## Capacidades (roles.yaml)

| Capacidade | Admin | Usuário |
|------------|:-----:|:-------:|
| `view_all_sessions` | ✓ | |
| `configure_connections` | ✓ | |
| `approve_connection_requests` | ✓ | |
| `configure_ldap` | ✓ | |
| `use_default_html_browser` | ✓ | ✓ |
| `request_new_connections` | ✓ | ✓ |
| `use_own_connections` | ✓ | ✓ |

---

## Isolamento de sessão

Cada conexão Guacamole é **individual**. O navegador padrão é um serviço compartilhado na rede interna, mas as sessões Guacamole/guacd permanecem por usuário. Terminais RDP/VNC/SSH extras só aparecem após liberação explícita.

---

## Seed / bootstrap

```bash
# Automático no compose e no Job K8s
docker compose -f docker-compose.dev.yml up --build

# Reaplicar (idempotente)
./scripts/bootstrap-segportal.sh
```

---

## Referências

- [CONNECTIONS.md](CONNECTIONS.md) — navegador padrão e pedidos
- [CONFIGURATION.md](CONFIGURATION.md)
- [MANUAL.md](MANUAL.md)
- `config/roles/roles.yaml`
