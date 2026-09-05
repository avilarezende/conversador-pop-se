# Portal Auth — SegPortal AQNE

Serviço FastAPI do **dashboard pessoal**: autenticação (local / Active Directory),
montagem de pastas corporativas indicadas pelo AD, OneDrive/Google Drive e
gerenciador de arquivos HTML.

## URLs

| Ambiente | URL |
|----------|-----|
| Compose local | http://localhost:8090 |
| Health | `GET /api/health` |

## Credenciais demo

| Usuário | Senha | Papel |
|---------|-------|-------|
| `usuario` | `usuario` | user |
| `guacadmin` | `guacadmin` | admin |

Marque **Autenticar via Active Directory** no login para simular sessão LDAP e
expor compartilhamentos AD (home, departamental) no dashboard.

## OneDrive / Google Drive

No painel **Início**, use **Montar**. Sem `client_id` em `config/files/shares.yaml`,
a montagem é em **modo demonstração** (pasta local sob `/data/shares/cloud/...`).
Com OAuth configurado, o portal redireciona ao provedor.

## Arquivos

- Configuração: `config/files/shares.yaml`
- Atributos AD: `homeDirectory`, `homeDrive`, `profilePath`, `extensionAttribute10`
- UI: `static/index.html` + `static/assets/`

## Desenvolvimento local (sem Docker)

```bash
cd services/portal-auth
pip install -r requirements.txt
DEMO_SHARES_ROOT=/tmp/segportal-shares uvicorn app.main:app --reload --port 8090
```

## Compose

O serviço `portal-auth` sobe com a stack em `docker-compose.yml` (porta **8090**).
