# Mockup e preview — SegPortal AQNE

Materiais visuais do portal para documentação e demonstração de papéis.

## Imagens JPG

| Arquivo | Conteúdo |
|---------|----------|
| [segportal-mockup.jpg](../images/segportal-mockup.jpg) | Login / capa |
| [usage-login.jpg](../images/usage-login.jpg) | Tela de login |
| [usage-portal.jpg](../images/usage-portal.jpg) | Dashboard (pastas AD e nuvem) |
| [usage-browser.jpg](../images/usage-browser.jpg) | Aba Navegador embutida |
| [usage-browser-bacen.jpg](../images/usage-browser-bacen.jpg) | Navegador no Bacen |
| [portal-sessions.jpg](../images/portal-sessions.jpg) | Aba Computadores |
| [usage-session.jpg](../images/usage-session.jpg) | Sessão de computador no portal |
| [admin-approvals.jpg](../images/admin-approvals.jpg) | Painel admin |
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
| Administrador | `admin` | `admin` | `123456` |
| Usuário | `usuario` | `usuario` | `123456` |

O usuário vê o **Navegador Web SegPortal** e pode simular pedido de terminal.  
O admin vê sessões globais, aprovações e configuração.

Manuais: [MANUAL.md](../MANUAL.md) · [USAGE.md](../USAGE.md) · [ROLES.md](../ROLES.md) · [CONNECTIONS.md](../CONNECTIONS.md)
