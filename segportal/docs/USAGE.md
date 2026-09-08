# Guia de uso — SegPortal AQNE

Fluxo visual do usuário final. Manuais completos: [USER_MANUAL.md](USER_MANUAL.md) · [MANUAL.md](MANUAL.md).

---

## Visão geral

![Mockup do portal](images/segportal-mockup.jpg)

1. Autenticar no dashboard (`:8090`) — local e/ou Active Directory (portal em destaque no login)  
2. Usar pastas AD e montar OneDrive/Google Drive  
3. Gerenciar arquivos no explorador HTML  
4. Usar o **navegador corporativo** embutido (proxy + política do admin)  
5. Abrir **computadores** remotos liberados ao perfil  
6. Organizar o dia com **lembretes arrastáveis** e **calendário** deslizante  
7. (Admin) Em **Administração**, criar acessos, alocar usuários e gerir o proxy  

---

## 1. Login

![Tela de login](images/usage-login.jpg)

| Campo | Produção | Demo local |
|-------|----------|------------|
| Usuário | `sAMAccountName` ou local | `usuario` / `admin` |
| Senha | AD / local | `usuario` / `admin` |
| Active Directory | Marque se for conta de domínio | Marque para ver shares demo AD |
| MFA | Se habilitado no SegPortal | Não exigido no compose.dev |

URLs demo: dashboard `http://localhost:8090` · SegPortal `http://localhost:8090`.

---

## 2. Dashboard pessoal

![Dashboard com AD e nuvem](images/usage-portal.jpg)

| Área | Uso |
|------|-----|
| **Arquivos do Active Directory** | Home, departamental, público |
| **Nuvem pessoal** | Montar/abrir OneDrive e Google Drive |
| **Acesso rápido** | Atalhos para arquivos e navegador web |
| **Abrir Computadores** | Abre a aba de desktops/aplicações no próprio SegPortal |
| **Navegador** | Navegação HTML5 embutida na mesma aba |
| **Lembretes** | Painel flutuante arrastável (posição memorizada) |
| **Calendário** | Aba lateral deslizante com Google Calendar / Microsoft Outlook |

### 2.1 Arquivos corporativos e nuvem

![Nuvem montada](images/portal-cloud-mounted.jpg)

1. Marque AD no login (quando aplicável)  
2. Em **Nuvem pessoal**, clique em **Montar**  
3. Em **Arquivos**, navegue, envie (arrastar/soltar), crie pastas  

![Gerenciador de arquivos](images/portal-files.jpg)

Detalhes: [FILES.md](FILES.md) · [USER_MANUAL.md](USER_MANUAL.md).

### 2.2 Lembretes e calendário

- **Lembretes**: painel flutuante disponível no login; arraste pelo cabeçalho para qualquer canto (posição salva por usuário).
- **Calendário**: aba lateral deslizante (botão **Calendário** ou aba na borda direita). Provedores: Google, Microsoft ou agenda local. Cole a URL pública de embed para conectar.

---

## 3. Navegador corporativo (aba Navegador)

![Navegador via proxy no SegPortal](images/usage-browser-proxy.jpg)

O **Navegador Web SegPortal** está embutido como aba do próprio portal. Digite URLs `https://…` na barra: o conteúdo é carregado pelo **proxy autenticado** (`/api/browser/proxy`), sujeito à política do administrador (allowlist, filtros, exceções e horários).

**Exemplo:** `https://www.bcb.gov.br/` (Bacen) ou `example.com` em laboratório.

![Navegador no Bacen](images/usage-browser-bacen.jpg)

### 3.1 Computadores

![Aba Computadores](images/portal-computers.jpg)

Use a aba **Computadores** ou o botão **Abrir Computadores** no Início. Desktops e aplicações liberados abrem **dentro do SegPortal**.

![Sessão de computador](images/usage-session.jpg)

### 3.2 Administração (somente admin)

![Política de proxy](images/portal-admin-proxy.jpg)

Na aba **Administração**:

1. **Proxy de navegação** — modos allowlist/blocklist, URLs permitidas/filtradas, exceções por usuário/AD e horários.
2. **Computadores** — criar acessos RDP/VNC/SSH e alocar a usuários locais ou do Active Directory.

![Criar computador](images/portal-admin-computers.jpg)

---

## 4. Pedido legado de computador adicional

```bash
./scripts/request-connection.sh usuario "RDP Financeiro" rdp 10.10.20.51 3389 "Justificativa"
./scripts/approve-connection-request.sh 1
```

![Visão admin](images/admin-approvals.jpg)

---

## 5. Encerramento

- **Fechar sessão** na aba Computadores  
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
| [usage-browser.jpg](images/usage-browser.jpg) | Aba Navegador embutida |
| [usage-browser-bacen.jpg](images/usage-browser-bacen.jpg) | Navegador no Bacen |
| [portal-sessions.jpg](images/portal-sessions.jpg) | Aba Computadores |
| [usage-session.jpg](images/usage-session.jpg) | Sessão de computador |
| [admin-approvals.jpg](images/admin-approvals.jpg) | Admin |
