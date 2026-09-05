# Guia de uso — SegPortal TJSE

Fluxo visual do usuário final. Manuais completos: [USER_MANUAL.md](USER_MANUAL.md) · [MANUAL.md](MANUAL.md).

---

## Visão geral

![Mockup do portal](images/segportal-mockup.jpg)

1. Autenticar no dashboard (`:8090`) — local e/ou Active Directory  
2. Usar pastas AD e montar OneDrive/Google Drive  
3. Gerenciar arquivos no explorador HTML  
4. Abrir sessões remotas (navegador HTML5, RDP, VNC, SSH)  
5. Se precisar de terminal extra, **solicitar** e aguardar o admin  

---

## 1. Login

![Tela de login](images/usage-login.jpg)

| Campo | Produção | Demo local |
|-------|----------|------------|
| Usuário | `sAMAccountName` ou local | `usuario` / `guacadmin` |
| Senha | AD / local | `usuario` / `guacadmin` |
| Active Directory | Marque se for conta de domínio | Marque para ver shares demo AD |
| MFA | Se habilitado no Guacamole | Não exigido no compose.dev |

URLs demo: dashboard `http://localhost:8090` · Guacamole `http://localhost:8080/guacamole`.

---

## 2. Dashboard pessoal

![Dashboard com AD e nuvem](images/usage-portal.jpg)

| Área | Uso |
|------|-----|
| **Arquivos do Active Directory** | Home, departamental, público |
| **Nuvem pessoal** | Montar/abrir OneDrive e Google Drive |
| **Acesso rápido** | Atalhos para arquivos e navegador web |
| **Abrir Guacamole** | Sessões remotas |

### 2.1 Arquivos corporativos e nuvem

![Nuvem montada](images/portal-cloud-mounted.jpg)

1. Marque AD no login (quando aplicável)  
2. Em **Nuvem pessoal**, clique em **Montar**  
3. Em **Arquivos**, navegue, envie (arrastar/soltar), crie pastas  

![Gerenciador de arquivos](images/portal-files.jpg)

Detalhes: [FILES.md](FILES.md) · [USER_MANUAL.md](USER_MANUAL.md).

---

## 3. Navegador HTML padrão (exemplo: site do Bacen)

![Navegador HTML5 no site do Bacen](images/usage-browser.jpg)

No boot, `web-browser` sobe e o bootstrap cria a conexão **Navegador Web SegPortal** para todos. O Firefox roda via VNC e é entregue em **HTML5** no Guacamole — sem cliente VPN.

**Exemplo de uso:** abra a sessão **Navegador Web SegPortal** e acesse `https://www.bcb.gov.br/` (Banco Central do Brasil). A navegação sai pelo `proxy-egress` com IP institucional, quando configurado.

![Sessão remota no Bacen](images/usage-session.jpg)

---

## 4. Pedido de terminal adicional

```bash
./scripts/request-connection.sh usuario "RDP Financeiro" rdp 10.10.20.51 3389 "Justificativa"
./scripts/approve-connection-request.sh 1
```

![Visão admin](images/admin-approvals.jpg)

---

## 5. Encerramento

- **Encerrar sessão** na conexão Guacamole  
- Timeout por inatividade  
- **Sair** no dashboard  

---

## Imagens

| Arquivo | Conteúdo |
|---------|----------|
| [segportal-mockup.jpg](images/segportal-mockup.jpg) | Login / capa |
| [usage-login.jpg](images/usage-login.jpg) | Login |
| [usage-portal.jpg](images/usage-portal.jpg) | Dashboard |
| [portal-files.jpg](images/portal-files.jpg) | Arquivos |
| [portal-cloud-mounted.jpg](images/portal-cloud-mounted.jpg) | Nuvem |
| [usage-browser.jpg](images/usage-browser.jpg) | Navegador HTML5 no Bacen |
| [usage-session.jpg](images/usage-session.jpg) | Sessão remota (mesmo exemplo) |
| [usage-browser-bacen.jpg](images/usage-browser-bacen.jpg) | Alias do exemplo Bacen |
| [admin-approvals.jpg](images/admin-approvals.jpg) | Admin |
