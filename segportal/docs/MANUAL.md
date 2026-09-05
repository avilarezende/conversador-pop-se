# Manual — SegPortal TJSE

Manual de referência do portal ZTNA do Tribunal de Justiça de Sergipe.

---

## Manuais por público

| Público | Documento |
|---------|-----------|
| **Usuário final** (passo a passo) | **[USER_MANUAL.md](USER_MANUAL.md)** |
| **Administrador** (operação e config) | **[ADMIN_MANUAL.md](ADMIN_MANUAL.md)** |
| Resumo visual | [USAGE.md](USAGE.md) |
| Arquivos AD / OneDrive / Google Drive | [FILES.md](FILES.md) |
| Navegador padrão e pedidos de terminal | [CONNECTIONS.md](CONNECTIONS.md) |
| Papéis admin / usuário | [ROLES.md](ROLES.md) |
| Admin local e LDAP opcional | [LOCAL_ADMIN.md](LOCAL_ADMIN.md) |
| Configuração técnica | [CONFIGURATION.md](CONFIGURATION.md) |

---

## 1. O que é o SegPortal?

O SegPortal permite acessar sistemas do TJSE e sites (internos e externos) **pelo navegador**, sem VPN. Inclui:

- **Dashboard pessoal** (`:8090`) — pastas do Active Directory, OneDrive/Google Drive e gerenciador HTML
- **Sessões remotas** (Guacamole `:8080`) — RDP, VNC, SSH e **Navegador Web SegPortal** (Firefox HTML5)

![Mockup do portal](images/segportal-mockup.jpg)

![Dashboard pessoal](images/portal-home-ad.jpg)

---

## 2. Acesso do usuário final

### 2.1 Login

1. Acesse **http://localhost:8090** (demo) ou a URL institucional.
2. Informe usuário/senha.
3. Marque **Active Directory** quando for conta de domínio (monta pastas liberadas).
4. Clique em **Entrar no portal**.

![Tela de login](images/usage-login.jpg)

**Demo local**

| Papel | Usuário | Senha |
|-------|---------|-------|
| Administrador | `guacadmin` | `guacadmin` |
| Usuário | `usuario` | `usuario` |

### 2.2 Depois do login

![Portal de recursos](images/usage-portal.jpg)

| Recurso | Onde |
|---------|------|
| Pastas AD | Início → cartões Active Directory |
| OneDrive / Google Drive | Início → Nuvem pessoal |
| Gerenciador de arquivos | Aba **Arquivos** |
| Navegador HTML5 / RDP / VNC / SSH | Aba **Sessões remotas** ou Guacamole |

Passo a passo completo: [USER_MANUAL.md](USER_MANUAL.md).

### 2.3 Arquivos

![Gerenciador de arquivos](images/portal-files.jpg)

Listar, enviar (arrastar e soltar), criar pasta, renomear, baixar e excluir. Detalhes: [FILES.md](FILES.md).

### 2.4 Navegador Web SegPortal (ex.: Bacen)

![Navegador HTML5 no Bacen](images/usage-browser.jpg)

Firefox via VNC em HTML5 — liberado automaticamente para todos no boot. Exemplo: na sessão remota, abra `https://www.bcb.gov.br/`. Ver [CONNECTIONS.md](CONNECTIONS.md) e [USAGE.md](USAGE.md).

![Painel de sessões](images/portal-sessions.jpg)

---

## 3. Administração

![Visão administrativa](images/portal-admin-home.jpg)

| Tema | Documento |
|------|-----------|
| Contas locais / senha guacadmin | [LOCAL_ADMIN.md](LOCAL_ADMIN.md) |
| Shares AD, OAuth nuvem, API | [ADMIN_MANUAL.md](ADMIN_MANUAL.md) · [FILES.md](FILES.md) |
| Papéis e aprovações | [ROLES.md](ROLES.md) · [CONNECTIONS.md](CONNECTIONS.md) |
| LDAP, MFA, K8s | [CONFIGURATION.md](CONFIGURATION.md) · [DEPLOYMENT.md](DEPLOYMENT.md) |

---

## 4. Arquitetura (resumo)

![Arquitetura](images/architecture-overview.jpg)

![Fluxo de autenticação](images/auth-flow.jpg)

| Componente | Porta | Função |
|------------|-------|--------|
| portal-auth | 8090 | Dashboard, arquivos AD/nuvem |
| guacamole | 8080 | Sessões remotas |
| guacd | 4822 | Proxy RDP/VNC/SSH |
| web-browser | 5900 | Firefox VNC |
| postgres | 5432 | Metadados |
| proxy-egress | 3128 | IP institucional |

---

## 5. Início rápido

```bash
cd segportal
cp .env.example .env
docker compose up --build
```

- Dashboard: http://localhost:8090  
- Guacamole: http://localhost:8080/guacamole  

Credenciais demo: `usuario`/`usuario` · `guacadmin`/`guacadmin`.
