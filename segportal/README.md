# SegPortal — Portal ZTNA do TJSE

[![CI](https://github.com/avilarezende/segportal/actions/workflows/ci.yml/badge.svg)](https://github.com/avilarezende/segportal/actions/workflows/ci.yml)

**SegPortal** é o portal de acesso seguro do **Tribunal de Justiça de Sergipe (TJSE)**. Baseado em [Apache Guacamole](https://guacamole.apache.org/), substitui a VPN interna por um modelo **ZTNA** (Zero Trust Network Access): autenticação local e/ou LDAP (`tjse.jus.br`) com MFA opcional, e acesso a RDP, VNC, SSH e navegação web **direto no navegador**, sem cliente VPN.

**Repositório:** https://github.com/avilarezende/segportal

---

## Para quem é este projeto

| Público | O que encontrar aqui |
|---------|----------------------|
| **Usuário final** | [Manual do usuário](docs/USER_MANUAL.md) · [guia visual](docs/USAGE.md) · [arquivos/nuvem](docs/FILES.md) |
| **Administrador** | [Manual do administrador](docs/ADMIN_MANUAL.md) · [Configuração](docs/CONFIGURATION.md) |
| **Infraestrutura** | [Deploy](docs/DEPLOYMENT.md) — Rancher, pods, secrets |
| **Desenvolvimento** | [Arquitetura](docs/ARCHITECTURE.md) e [CI/CD](docs/CI_CD.md) |

---

## Mockup do portal

![Mockup SegPortal TJSE](docs/images/segportal-mockup.jpg)

*Login, portal com navegador HTML padrão, sessão clientless e painel admin de aprovações.*

Preview interativo: [docs/mockup/segportal-preview.html](docs/mockup/segportal-preview.html)

---

## Arquitetura

![Diagrama de arquitetura](docs/images/architecture-overview.jpg)

| Componente | Função | Pod K8s |
|------------|--------|---------|
| **Guacamole** | Portal web, autenticação e autorização | `guacamole` (HPA 2–10) |
| **guacd** | Proxy RDP, VNC e SSH | `guacd` (HPA 2–20) |
| **PostgreSQL** | Metadados de conexões e sessões | `postgres` (StatefulSet) |
| **Proxy egress** | Navegação HTTP com IP institucional TJSE | `proxy-egress` (HPA 1–5) |
| **Web browser** | Firefox via VNC — navegador HTML **padrão** | `web-browser` (HPA 2–10) |
| **Portal auth** | Dashboard pessoal: AD shares, OneDrive/Google Drive, file manager | `portal-auth` |
| **Bootstrap** | Conexão padrão + papéis no banco | Job `segportal-bootstrap` |

![Fluxo de autenticação](docs/images/auth-flow.jpg)

![Pods Kubernetes](docs/images/k8s-pods.jpg)

---

## Exemplos de uso

| Etapa | Imagem | Descrição |
|-------|--------|-----------|
| **1. Login** | ![Login](docs/images/usage-login.jpg) | Credenciais locais ou AD (+ MFA no Guacamole, se habilitado) |
| **2. Dashboard** | ![Portal](docs/images/usage-portal.jpg) | Pastas AD, OneDrive/Google Drive e atalhos |
| **3. Arquivos** | ![Arquivos](docs/images/portal-files.jpg) | Gerenciador HTML (upload, pastas, nuvem) |
| **4. Navegador HTML5** | ![Bacen](docs/images/usage-browser.jpg) | Firefox no portal acessando o site do **Bacen** (`bcb.gov.br`) |
| **5. Sessão / Admin** | ![Admin](docs/images/portal-admin-home.jpg) | Sessões remotas e visão administrativa |

---

## Início rápido (desenvolvimento local)

### Pré-requisitos

- Docker e Docker Compose v2
- Git

### Passos

```bash
git clone https://github.com/avilarezende/segportal.git
cd segportal
cp .env.example .env
# Edite .env (PostgreSQL; LDAP/RADIUS se for usar)
docker compose up --build
```

Acesse:
- **Dashboard pessoal (arquivos AD + nuvem):** http://localhost:8090  
- **Guacamole (sessões remotas):** http://localhost:8080/guacamole

No primeiro boot o serviço `segportal-bootstrap` cria schema (se preciso), papéis e a conexão **Navegador Web SegPortal** (Firefox via VNC) liberada para todos. Demo sem LDAP:

```bash
docker compose -f docker-compose.dev.yml up --build
# guacadmin / guacadmin  ·  usuario / usuario
```

Detalhes: [docs/CONNECTIONS.md](docs/CONNECTIONS.md)

### Deploy em produção (Kubernetes / Rancher)

```bash
# 1. Criar secrets (ver docs/CONFIGURATION.md)
kubectl apply -k k8s/overlays/production
# Job segportal-bootstrap aplica navegador padrão automaticamente
```

---

## Configuração essencial

| Item | Arquivo / variável | Detalhes |
|------|-------------------|----------|
| **Papéis admin / usuário** | `config/roles/roles.yaml` | [ROLES.md](docs/ROLES.md) |
| **Admin local padrão** | `guacadmin` / `guacadmin` | [LOCAL_ADMIN.md](docs/LOCAL_ADMIN.md) |
| LDAP (opcional) | `LDAP_ENABLED`, `config/ldap/ldap-settings.yaml` | [CONFIGURATION.md](docs/CONFIGURATION.md#3-active-directory-ldap--opcional) |
| MFA RADIUS | `MFA_RADIUS_HOST`, `MFA_RADIUS_SECRET` | [CONFIGURATION.md](docs/CONFIGURATION.md#4-mfa-via-radius) |
| Navegador padrão | `web-browser` + bootstrap | [CONNECTIONS.md](docs/CONNECTIONS.md) |
| Sessões | `SESSION_TIMEOUT_MINUTES` | Timeout e limite de conexões |
| Proxy egress | `config/proxy/squid.conf` | Whitelist de domínios externos |
| Secrets K8s | `k8s/*/secret.example.yaml` | Copiar e preencher antes do deploy |

Guia passo a passo: **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)**

---

## Estrutura do repositório

```
segportal/
├── config/              # guacamole.properties, LDAP, Squid, papéis
├── docs/
│   ├── images/          # diagramas e mockups (JPG)
│   ├── mockup/          # preview HTML interativo
│   ├── MANUAL.md        # manual usuário + admin
│   ├── USAGE.md         # guia visual de uso
│   ├── CONFIGURATION.md # configuração
│   └── ...
├── k8s/                 # manifests Kubernetes modulares
│   ├── web-browser/     # Firefox padrão
│   ├── bootstrap/       # Job de seed automático
│   └── overlays/
├── services/            # Dockerfiles por componente
├── scripts/             # bootstrap, pedidos, admin local
└── tests/               # validação automatizada
```

---

## Segurança

- Autenticação **local** sempre disponível (admin `guacadmin` independente do LDAP)
- LDAP **opcional** — apontamentos configuráveis pelo administrador
- MFA via RADIUS quando habilitado
- Navegador HTML padrão com VNC **somente na rede interna**
- Pedidos de terminal exigem **aprovação do admin**
- Sessões **individualizadas** por usuário
- **NetworkPolicies** isolam pods no Kubernetes
- TLS obrigatório em produção

Detalhes: [docs/SECURITY.md](docs/SECURITY.md) · [docs/LOCAL_ADMIN.md](docs/LOCAL_ADMIN.md)

---

## Documentação completa

| Documento | Conteúdo |
|-----------|----------|
| [MANUAL.md](docs/MANUAL.md) | Manual do usuário e administrador |
| [USAGE.md](docs/USAGE.md) | Fluxo de uso com imagens |
| [LOCAL_ADMIN.md](docs/LOCAL_ADMIN.md) | Admin padrão, senha, exclusão e LDAP opcional |
| [ROLES.md](docs/ROLES.md) | Papéis admin e usuário (RBAC) |
| [CONNECTIONS.md](docs/CONNECTIONS.md) | Navegador padrão e pedidos de terminais |
| [CONFIGURATION.md](docs/CONFIGURATION.md) | Configuração LDAP, MFA, proxy e K8s |
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura e decisões de design |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Deploy no Rancher |
| [SECURITY.md](docs/SECURITY.md) | Controles de segurança |
| [CI_CD.md](docs/CI_CD.md) | Pipelines GitHub Actions |

---

## Contribuição

Leia [CONTRIBUTING.md](CONTRIBUTING.md) antes de abrir pull requests.

## Licença

Uso interno TJSE. Consulte a área de TI para termos de distribuição.
