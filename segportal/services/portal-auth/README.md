# Portal Auth — SegPortal AQNE

Serviço FastAPI do **dashboard pessoal**: autenticação (local / Active Directory),
pastas corporativas do AD, OneDrive/Google Drive, gerenciador de arquivos HTML,
**navegador corporativo com proxy**, **computadores alocáveis** e
**administração** (proxy + acessos).

## URLs

| Ambiente | URL |
|----------|-----|
| Compose local | http://localhost:8090 |
| Health | `GET /api/health` |

## Credenciais demo

| Usuário | Senha | Papel |
|---------|-------|-------|
| `usuario` | `usuario` | user |
| `admin` | `admin` | admin |

Marque **Autenticar via Active Directory** no login para simular sessão LDAP e
expor compartilhamentos AD (home, departamental) no dashboard.

## Recursos

| Área | Descrição |
|------|-----------|
| **Início** | Shares AD, nuvem, atalhos, lembretes/calendário |
| **Arquivos** | Explorador HTML (upload, pastas, nuvem) |
| **Navegador** | Proxy autenticado `/api/browser/proxy` + política admin |
| **Computadores** | Acessos liberados ao perfil (`computers.json`) |
| **Administração** | Criar/alocar PCs + política de proxy (só admin) |

## OneDrive / Google Drive

No painel **Início**, use **Montar**. Sem `client_id` em `config/files/shares.yaml`,
a montagem é em **modo demonstração** (pasta local sob `/data/shares/cloud/...`).
Com OAuth configurado, o portal redireciona ao provedor.

## Persistência demo

| Arquivo | Conteúdo |
|---------|----------|
| `{DEMO_SHARES_ROOT}/computers.json` | Acessos a computadores e assignees |
| `{DEMO_SHARES_ROOT}/proxy_policy.json` | Allowlist, filtros, exceções, horários |

## API (trecho)

| Método | Rota |
|--------|------|
| `GET` | `/api/computers` |
| `GET/POST/PATCH/DELETE` | `/api/admin/computers` |
| `GET/PUT` | `/api/admin/proxy-policy` |
| `GET` | `/api/browser/proxy?url=` |

## Arquivos

- Configuração: `config/files/shares.yaml`
- Atributos AD: `homeDirectory`, `homeDrive`, `profilePath`, `extensionAttribute10`
- UI: `static/index.html` + `static/assets/`
- Módulos: `app/computers.py`, `app/proxy_policy.py`, `app/browser_proxy.py`

## Desenvolvimento local (sem Docker)

```bash
cd services/portal-auth
pip install -r requirements.txt
DEMO_SHARES_ROOT=/tmp/segportal-shares uvicorn app.main:app --reload --port 8090
```

## Compose

O serviço `portal-auth` sobe com a stack em `docker-compose.yml` (porta **8090**).
