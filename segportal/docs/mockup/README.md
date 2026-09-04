# Mockup e preview — SegPortal TJSE

Materiais visuais do portal para documentação e demonstração de papéis.

## Imagens JPG

| Arquivo | Conteúdo |
|---------|----------|
| [segportal-mockup.jpg](../images/segportal-mockup.jpg) | Visão geral: login, portal, sessão, admin |
| [usage-login.jpg](../images/usage-login.jpg) | Tela de login |
| [usage-portal.jpg](../images/usage-portal.jpg) | Lista de recursos (navegador padrão em destaque) |
| [usage-browser.jpg](../images/usage-browser.jpg) | Fluxo do navegador HTML automático |
| [usage-session.jpg](../images/usage-session.jpg) | Sessão Firefox clientless |
| [admin-approvals.jpg](../images/admin-approvals.jpg) | Painel admin (sessões e aprovações) |
| [architecture-overview.jpg](../images/architecture-overview.jpg) | Arquitetura ZTNA |
| [auth-flow.jpg](../images/auth-flow.jpg) | Fluxo de autenticação |
| [k8s-pods.jpg](../images/k8s-pods.jpg) | Pods Kubernetes |

## Preview interativo (HTML)

```bash
cd docs/mockup
python3 -m http.server 8765
# http://localhost:8765/segportal-preview.html
```

| Papel | Login | Senha | MFA |
|-------|-------|-------|-----|
| Administrador | `guacadmin` | `guacadmin` | `123456` |
| Usuário | `usuario` | `usuario` | `123456` |

O usuário vê o **Navegador Web SegPortal** e pode simular pedido de terminal.  
O admin vê sessões globais, aprovações e configuração.

Manuais: [MANUAL.md](../MANUAL.md) · [USAGE.md](../USAGE.md) · [ROLES.md](../ROLES.md) · [CONNECTIONS.md](../CONNECTIONS.md)
