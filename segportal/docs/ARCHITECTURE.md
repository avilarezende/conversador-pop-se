# Arquitetura — SegPortal TJSE

SegPortal implementa **ZTNA (Zero Trust Network Access)** para o TJSE com Apache Guacamole como portal clientless HTML5.

## Visão geral

![Arquitetura](images/architecture-overview.jpg)

| Componente | Função | Serviço / pod |
|------------|--------|----------------|
| **portal-auth** | Dashboard pessoal: AD shares, OneDrive/Google Drive, file manager HTML | `portal-auth` (`:8090`) |
| **Guacamole** | Portal web, autenticação e autorização de sessões | `guacamole` (`:8080`) |
| **guacd** | Proxy de protocolos RDP, VNC e SSH | `guacd` |
| **web-browser** | Firefox via VNC — navegador HTML **padrão** | `web-browser` |
| **proxy-egress** | Squid — HTTP(S) com IP institucional | `proxy-egress` |
| **PostgreSQL** | Metadados de conexões, usuários e sessões | `postgres` |
| **Bootstrap** | Seed idempotente: papéis + navegador padrão | `segportal-bootstrap` |

## Fluxo de autenticação

![Fluxo LDAP + MFA](images/auth-flow.jpg)

1. Usuário acessa o **portal-auth** (`:8090`) e/ou o Guacamole
2. Autentica via **conta local** e/ou **LDAP/AD** (`tjse.jus.br`), conforme configuração
3. No dashboard, recebe pastas AD e opção de montar OneDrive/Google Drive
4. MFA via **RADIUS** no Guacamole se `MFA_ENABLED=true`
5. Sessões remotas: no mínimo o **Navegador Web SegPortal**

## Deploy Kubernetes

![Pods K8s](images/k8s-pods.jpg)

| Workload | Escala típica |
|----------|---------------|
| `portal-auth` | HPA 2–6 |
| `guacamole` | HPA 2–10 |
| `guacd` | HPA 2–20 |
| `web-browser` | HPA 2–10 |
| `proxy-egress` | HPA 1–5 |
| `postgres` | StatefulSet 1 |
| `segportal-bootstrap` | Job (uma execução por deploy/boot) |

## Mockup do portal

![Mockup](images/segportal-mockup.jpg)

## Modularidade

```
segportal/
├── services/portal-auth/   # Dashboard AD/nuvem + file manager (:8090)
├── services/guacamole/     # Portal + entrypoint LDAP opcional
├── services/guacd/         # Daemon de protocolos
├── services/web-browser/   # Firefox via VNC
├── services/egress-proxy/  # Squid
├── config/files/shares.yaml
├── scripts/bootstrap-segportal.sh
├── scripts/capture-portal-docs.py
├── k8s/web-browser/
├── k8s/bootstrap/
└── k8s/overlays/
```

## Decisões de design

| Decisão | Motivo |
|---------|--------|
| portal-auth separado | UI de arquivos/AD/nuvem sem acoplar ao Guacamole Java |
| Guacamole 1.5.5 | Base estável com JDBC + LDAP oficiais |
| Navegador padrão no boot | Todo usuário navega sem VPN desde o primeiro login |
| Bootstrap automático | Elimina seed manual e drift de configuração |
| Pedidos com aprovação | Usuário não cria conexões sozinho |
| LDAP opcional | Homologação e emergência sem AD |
| Pods separados | Escala e blast radius independentes |
| Squid whitelist | Egress controlado no lugar da VPN HTTP |

## Referências

- [USER_MANUAL.md](USER_MANUAL.md) · [ADMIN_MANUAL.md](ADMIN_MANUAL.md)
- [FILES.md](FILES.md) · [CONNECTIONS.md](CONNECTIONS.md)
- [ROLES.md](ROLES.md) · [CONFIGURATION.md](CONFIGURATION.md)
- [DEPLOYMENT.md](DEPLOYMENT.md) · [SECURITY.md](SECURITY.md)
- [CI_CD.md](CI_CD.md)- [CONFIGURATION.md](CONFIGURATION.md)
- [DEPLOYMENT.md](DEPLOYMENT.md)
- [SECURITY.md](SECURITY.md)
