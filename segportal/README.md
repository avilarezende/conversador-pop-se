# SegPortal — Portal ZTNA do TJSE

[![CI](https://github.com/avilarezende/segportal/actions/workflows/ci.yml/badge.svg)](https://github.com/avilarezende/segportal/actions/workflows/ci.yml)

**SegPortal** é o portal de acesso seguro do **Tribunal de Justiça de Sergipe (TJSE)**. Baseado em [Apache Guacamole](https://guacamole.apache.org/), substitui a VPN interna por um modelo **ZTNA** (Zero Trust Network Access): o usuário autentica no domínio `tjse.jus.br` com **LDAP + MFA** e acessa recursos internos (RDP, VNC, SSH) ou sites externos **direto no navegador**, sem instalar cliente VPN.

**Repositório:** https://github.com/avilarezende/segportal

---

## Para quem é este projeto

| Público | O que encontrar aqui |
|---------|----------------------|
| **Usuário final** | [Manual de uso](docs/MANUAL.md) — login, recursos e sessões |
| **Administrador** | [Configuração](docs/CONFIGURATION.md) — LDAP, MFA, proxy, K8s |
| **Infraestrutura** | [Deploy](docs/DEPLOYMENT.md) — Rancher, pods, secrets |
| **Desenvolvimento** | [Arquitetura](docs/ARCHITECTURE.md) e [CI/CD](docs/CI_CD.md) |

---

## Mockup do portal

![Mockup SegPortal TJSE](docs/images/segportal-mockup.jpg)

*Telas de login (LDAP+MFA), portal de recursos e sessão clientless no navegador.*

---

## Arquitetura

![Diagrama de arquitetura](docs/images/architecture-overview.jpg)

| Componente | Função | Pod K8s |
|------------|--------|---------|
| **Guacamole** | Portal web, autenticação e autorização | `guacamole` (HPA 2–10) |
| **guacd** | Proxy de protocolos RDP, VNC e SSH | `guacd` (HPA 2–20) |
| **PostgreSQL** | Metadados de conexões e sessões | `postgres` (StatefulSet) |
| **Proxy egress** | Navegação HTTP com IP institucional TJSE | `proxy-egress` (HPA 1–5) |
| **Web browser** | Firefox via VNC — navegador HTML padrão | `web-browser` (HPA 2–10) |
| **Bootstrap** | Conexão padrão + papéis no banco | Job `segportal-bootstrap` |

![Fluxo de autenticação LDAP + MFA](docs/images/auth-flow.jpg)

---

## Exemplos de uso

| Etapa | Imagem | Descrição |
|-------|--------|-----------|
| **1. Login** | ![Login](docs/images/usage-login.jpg) | Credenciais do domínio `tjse.jus.br` + código MFA |
| **2. Portal** | ![Portal](docs/images/usage-portal.jpg) | Recursos liberados pelo grupo AD do usuário |
| **3. Sessão** | ![Sessão](docs/images/usage-session.jpg) | Desktop remoto no navegador, sem VPN |

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
# Edite .env com credenciais de homologação (LDAP, PostgreSQL, RADIUS)
docker compose up --build
```

Acesse: **http://localhost:8080/guacamole**

No primeiro boot o serviço `segportal-bootstrap` cria o schema (se preciso), papéis e a conexão **Navegador Web SegPortal** (Firefox via VNC) liberada para todos. Demo sem LDAP:

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
| Sessões | `SESSION_TIMEOUT_MINUTES` | Timeout e limite de conexões |
| Proxy egress | `config/proxy/squid.conf` | Whitelist de domínios externos |
| Secrets K8s | `k8s/*/secret.example.yaml` | Copiar e preencher antes do deploy |

Guia passo a passo completo: **[docs/CONFIGURATION.md](docs/CONFIGURATION.md)**

---

## Estrutura do repositório

```
segportal/
├── config/              # guacamole.properties, LDAP, Squid
├── docs/
│   ├── images/          # diagramas e mockups (JPG)
│   ├── MANUAL.md        # manual do usuário
│   ├── CONFIGURATION.md # guia de configuração
│   └── ARCHITECTURE.md  # arquitetura técnica
├── k8s/                 # manifests Kubernetes modulares
│   ├── guacamole/       # pod da interface web
│   ├── guacd/           # pod RDP/VNC/SSH
│   ├── postgres/        # banco de metadados
│   ├── proxy-egress/    # proxy de saída
│   └── overlays/        # dev, staging, production
├── services/            # Dockerfiles por componente
├── plugins/             # extensões Guacamole futuras
└── tests/               # validação automatizada (28 testes)
```

---

## Segurança

- Autenticação **local** sempre disponível (admin `guacadmin` independente do LDAP)
- LDAP **opcional** — apontamentos configuráveis pelo administrador
- MFA via RADIUS quando habilitado
- Sessões **individualizadas** por usuário
- **NetworkPolicies** isolam pods no Kubernetes
- TLS obrigatório em produção
- Secrets nunca commitados no repositório

Detalhes: [docs/SECURITY.md](docs/SECURITY.md) · [docs/LOCAL_ADMIN.md](docs/LOCAL_ADMIN.md)

---

## Documentação completa

| Documento | Conteúdo |
|-----------|----------|
| [MANUAL.md](docs/MANUAL.md) | Manual do usuário e administrador |
| [LOCAL_ADMIN.md](docs/LOCAL_ADMIN.md) | Admin padrão, senha, exclusão e LDAP opcional |
| [ROLES.md](docs/ROLES.md) | Papéis admin e usuário (RBAC) |
| [CONNECTIONS.md](docs/CONNECTIONS.md) | Navegador padrão e pedidos de terminais |
| [USAGE.md](docs/USAGE.md) | Fluxo de uso com exemplos visuais |
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
