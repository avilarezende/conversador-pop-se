# Guia de uso — SegPortal TJSE

Fluxo visual do usuário final. Manual completo: [MANUAL.md](MANUAL.md).

---

## Visão geral

![Mockup do portal](images/segportal-mockup.jpg)

1. Autenticar no portal (local e/ou LDAP + MFA opcional)
2. Ver recursos liberados — **sempre** inclui o Navegador Web SegPortal
3. Conectar no navegador HTML5 (sem VPN)
4. Se precisar de RDP/VNC/SSH extra, **solicitar** e aguardar aprovação do admin

---

## 1. Login

Acesse `https://segportal.tjse.jus.br` (ou `http://localhost:8080/guacamole` na demo).

![Tela de login](images/usage-login.jpg)

| Campo | Produção | Demo local |
|-------|----------|------------|
| Usuário | `sAMAccountName` do AD ou local | `usuario` ou `guacadmin` |
| Senha | AD / local | `usuario` / `guacadmin` |
| MFA | Se habilitado | Não exigido no compose.dev |

---

## 2. Portal de recursos

![Portal de recursos](images/usage-portal.jpg)

| Tipo | Uso |
|------|-----|
| **Navegador Web SegPortal** | Firefox HTML5 — **padrão automático para todos** |
| **RDP / VNC / SSH** | Terminais liberados por grupo ou após aprovação |

---

## 3. Navegador HTML padrão

![Fluxo do navegador padrão](images/usage-browser.jpg)

No boot, o serviço `web-browser` sobe e o `segportal-bootstrap` cria a conexão com `READ` para todos. Não há seed manual.

![Sessão clientless](images/usage-session.jpg)

Tráfego externo passa pelo `proxy-egress` (IP institucional TJSE), quando configurado.

---

## 4. Pedido de terminal adicional

Usuário solicita → admin aprova → conexão aparece só para o solicitante.

```bash
./scripts/request-connection.sh usuario "RDP Financeiro" rdp 10.10.20.51 3389 "Justificativa"
```

Admin:

```bash
./scripts/approve-connection-request.sh 1
```

![Painel de aprovações](images/admin-approvals.jpg)

---

## 5. Encerramento

- **Encerrar sessão** no menu da conexão
- Timeout por inatividade
- Logout do portal

---

## Diagramas e imagens

| Imagem | Conteúdo |
|--------|----------|
| [segportal-mockup.jpg](images/segportal-mockup.jpg) | Visão geral das telas |
| [usage-login.jpg](images/usage-login.jpg) | Login |
| [usage-portal.jpg](images/usage-portal.jpg) | Lista de recursos |
| [usage-browser.jpg](images/usage-browser.jpg) | Navegador padrão |
| [usage-session.jpg](images/usage-session.jpg) | Sessão HTML5 |
| [admin-approvals.jpg](images/admin-approvals.jpg) | Aprovações admin |
| [architecture-overview.jpg](images/architecture-overview.jpg) | Arquitetura |
| [auth-flow.jpg](images/auth-flow.jpg) | Autenticação |
| [k8s-pods.jpg](images/k8s-pods.jpg) | Pods Kubernetes |

Preview interativo: [mockup/segportal-preview.html](mockup/segportal-preview.html)
