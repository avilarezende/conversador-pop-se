# Guia de uso — SegPortal TJSE

Fluxo do usuário final com exemplos visuais. Para manual completo, veja [MANUAL.md](MANUAL.md).

---

## Visão geral

![Mockup do portal](images/segportal-mockup.jpg)

1. Usuário autentica no portal (LDAP + MFA)
2. Visualiza recursos liberados pelo grupo AD
3. Conecta via RDP, VNC ou SSH no navegador
4. (Opcional) Acessa sites externos via proxy com IP TJSE

---

## 1. Login no portal

Acesse `https://segportal.tjse.jus.br` e informe:

1. **Usuário** — `sAMAccountName` do domínio `tjse.jus.br`
2. **Senha** — credencial do Active Directory
3. **Código MFA** — token do autenticador ou RADIUS corporativo

![Tela de login](images/usage-login.jpg)

Após autenticação, o Guacamole emite token de sessão com timeout de 60 minutos (inatividade).

---

## 2. Portal de recursos

O usuário vê apenas conexões permitidas pelos **grupos AD**:

![Portal de recursos](images/usage-portal.jpg)

| Tipo | Uso típico |
|------|------------|
| **RDP** | Estações Windows, servidores de aplicação |
| **VNC** | Terminais Linux, consulta processual |
| **SSH** | Administração de servidores |
| **Proxy** | Sites externos com IP do tribunal |

---

## 3. Sessão clientless

Ao clicar em **Conectar**, o desktop remoto abre no navegador — sem VPN ou cliente RDP:

![Sessão ativa](images/usage-session.jpg)

Cada sessão é **individualizada**: processo guacd dedicado por usuário.

---

## 4. Navegação externa (egress)

Tráfego HTTP/HTTPS autorizado passa pelo pod `proxy-egress` e sai com **IP institucional** do TJSE.

![Arquitetura](images/architecture-overview.jpg)

---

## 5. Fluxo de autenticação

![Fluxo LDAP + MFA](images/auth-flow.jpg)

---

## 6. Encerramento de sessão

- **Logout** manual no menu
- **Timeout** por inatividade
- **Limite** de sessões simultâneas por usuário

---

## Diagramas adicionais

| Diagrama | Arquivo |
|----------|---------|
| Arquitetura completa | [architecture-overview.jpg](images/architecture-overview.jpg) |
| Fluxo de autenticação | [auth-flow.jpg](images/auth-flow.jpg) |
| Pods Kubernetes | [k8s-pods.jpg](images/k8s-pods.jpg) |
| Mockup do portal | [segportal-mockup.jpg](images/segportal-mockup.jpg) |

## Perfis e grupos AD

| Grupo AD | Recursos |
|----------|----------|
| `GG-SegPortal-Financeiro` | RDP estações financeiro |
| `GG-SegPortal-Consulta` | VNC terminais processuais |
| `GG-SegPortal-Admin` | SSH servidores + proxy egress |

Configuração: [CONFIGURATION.md](CONFIGURATION.md)
