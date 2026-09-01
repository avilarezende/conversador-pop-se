# SegPortal — Portal ZTNA do TJSE

[![CI](https://github.com/avilarezende/segportal/actions/workflows/ci.yml/badge.svg)](https://github.com/avilarezende/segportal/actions/workflows/ci.yml)

**SegPortal** é um portal de acesso seguro baseado em [Apache Guacamole](https://guacamole.apache.org/) para o **Tribunal de Justiça de Sergipe (TJSE)**. Substitui a VPN interna por acesso **clientless** (navegador HTML5), com autenticação **LDAP** no domínio `tjse.jus.br`, **MFA** obrigatório e sessões individualizadas.

## Diagrama de arquitetura

![Arquitetura SegPortal](docs/images/architecture-overview.svg)

## Fluxo de autenticação

![Fluxo LDAP + MFA](docs/images/auth-flow.svg)

## Exemplos de uso

| Tela | Descrição |
|------|-----------|
| [Login LDAP + MFA](docs/images/usage-login.png) | Autenticação no domínio `tjse.jus.br` com segundo fator |
| [Portal de recursos](docs/images/usage-portal.png) | Conexões RDP/VNC/SSH e navegação externa autorizadas |
| [Sessão clientless](docs/images/usage-session.png) | Desktop remoto no navegador via Guacamole |

Mockup interativo: [docs/mockup/segportal-mockup.html](docs/mockup/segportal-mockup.html)

## O que o SegPortal faz

| Capacidade | Descrição |
|------------|-----------|
| **ZTNA** | Acesso zero-trust: autenticação forte antes de qualquer recurso |
| **Clientless** | RDP, VNC e SSH direto no navegador |
| **LDAP + MFA** | Active Directory TJSE + segundo fator via RADIUS |
| **Egress controlado** | Proxy interno com IP institucional do tribunal |
| **Modular** | Pods separados, plugins futuros, HPA no Rancher |

## Guia rápido

```bash
git clone https://github.com/avilarezende/segportal.git
cd segportal
cp .env.example .env
docker compose up -d
# http://localhost:8080/guacamole
```

Deploy Kubernetes:

```bash
kubectl apply -k k8s/overlays/production
```

## Documentação

| Documento | Conteúdo |
|-----------|----------|
| [ARCHITECTURE.md](docs/ARCHITECTURE.md) | Arquitetura e componentes |
| [USAGE.md](docs/USAGE.md) | Guia de uso com diagramas e exemplos |
| [CONFIGURATION.md](docs/CONFIGURATION.md) | LDAP, MFA, Guacamole, proxy |
| [DEPLOYMENT.md](docs/DEPLOYMENT.md) | Rancher / Kubernetes |
| [SECURITY.md](docs/SECURITY.md) | Controles de segurança |
| [CI_CD.md](docs/CI_CD.md) | Pipelines GitHub Actions |

## Estrutura

```
segportal/
├── config/           # guacamole.properties, LDAP, proxy
├── docs/             # diagramas, imagens, mockup
├── k8s/              # manifests modulares + HPA
├── plugins/          # extensões Guacamole futuras
├── services/         # guacamole, guacd, egress-proxy
└── tests/            # validação de config e K8s
```

## Contribuição

Leia [CONTRIBUTING.md](CONTRIBUTING.md).

## Licença

Uso interno TJSE. Consulte a área de TI para termos de distribuição.
