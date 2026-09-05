# Manual do usuário — SegPortal AQNE

Guia prático para **servidores, magistrados e colaboradores** que usam o SegPortal no dia a dia.

Documentos relacionados: [USAGE.md](USAGE.md) (resumo visual) · [FILES.md](FILES.md) (arquivos/nuvem) · [MANUAL.md](MANUAL.md) (visão geral).

---

## 1. O que você consegue fazer

| Função | Onde | Para quê |
|--------|------|----------|
| Entrar com conta local ou **Active Directory** | Dashboard `:8090` | Autenticar e liberar pastas do AD |
| Abrir pastas corporativas (home, departamental, público) | **Início** → Arquivos do AD | Trabalhar em compartilhamentos liberados |
| Montar **OneDrive** e/ou **Google Drive** | **Início** → Nuvem pessoal | Acessar arquivos pessoais na nuvem |
| Gerenciar arquivos (enviar, pasta, renomear, baixar, excluir) | Aba **Arquivos** | Explorar como no Windows/macOS |
| Abrir o **navegador corporativo** (HTML5 embutido) | Aba **Navegador** | Navegar sem sair do SegPortal |
| Abrir **computadores** e desktops liberados | Aba **Computadores** ou botão **Abrir Computadores** | Usar estações remotas sem VPN |
| Solicitar computador/aplicação adicional | Pedido + aprovação do admin | RDP/VNC/SSH sob demanda |

---

## 2. Como entrar

![Tela de login do SegPortal](images/usage-login.jpg)

1. Abra o navegador e acesse o **dashboard pessoal**:
   - Local: `http://localhost:8090`
   - Produção: URL institucional do SegPortal (ingress)
2. Informe **usuário** e **senha**.
3. Se for conta de domínio, marque **Autenticar via Active Directory** (monta as pastas do AD no seu dashboard).
4. Clique em **Entrar no portal**.

**Demo local**

| Usuário | Senha | Perfil |
|---------|-------|--------|
| `usuario` | `usuario` | Usuário padrão |
| `admin` | `admin` | Administrador |

Sessões remotas (RDP/VNC/navegador HTML5): `http://localhost:8090`.

---

## 3. Dashboard pessoal (Início)

![Dashboard com pastas AD e nuvem](images/portal-home-ad.jpg)

Após o login você vê:

1. **Arquivos do Active Directory** — cartões com home, departamental e público (quando liberados).
2. **Nuvem pessoal** — OneDrive e Google Drive para montar ou abrir.
3. **Acesso rápido** — atalhos para o gerenciador de arquivos e o navegador web do SegPortal.
4. Botão **Abrir Computadores** — abre a aba de desktops e aplicações remotas no próprio SegPortal.

### 3.1 Abrir uma pasta do AD

1. No cartão desejado (ex.: **Meu Home (AD)**), clique em **Abrir**.
2. O SegPortal abre a aba **Arquivos** com o conteúdo da pasta.

### 3.2 Montar OneDrive ou Google Drive

1. Em **Nuvem pessoal**, clique em **Montar**.
2. Sem OAuth configurado, o portal usa **modo demonstração** (pasta local de exemplo).
3. Com `client_id` em `config/files/shares.yaml`, o navegador redireciona ao provedor.
4. Depois de montado, use **Abrir** ou a seção **Nuvem** na aba Arquivos.

![Nuvem montada](images/portal-cloud-mounted.jpg)

---

## 4. Gerenciador de arquivos

![Gerenciador de arquivos](images/portal-files.jpg)

### Locais (coluna esquerda)

- **Locais** — shares do AD / corporativos
- **Nuvem** — OneDrive / Google Drive montados

### Ações principais

| Ação | Como |
|------|------|
| Entrar em pasta | Clique no nome da pasta |
| Voltar | Botão **↑** |
| Nova pasta | **Nova pasta** → informe o nome no diálogo |
| Enviar arquivos | **Enviar** ou arraste para a área da lista |
| Baixar | **Baixar** na linha do arquivo |
| Renomear | **Renomear** → diálogo de nome |
| Excluir | **Excluir** → confirme |

![Nova pasta criada](images/portal-files-folder.jpg)

Dicas:

- Pastas marcadas como somente leitura (ex.: público) não permitem envio/exclusão.
- O tamanho máximo de upload segue `ui.max_upload_mb` em `shares.yaml` (padrão 100 MB).

---

## 5. Navegador e Computadores

![Aba Navegador embutida](images/usage-browser.jpg)

### 5.1 Navegador (aba própria)

1. Clique em **Navegador** na barra superior.
2. O navegador corporativo abre **embutido na mesma aba** do SegPortal (não há redirecionamento para outro sistema).
3. Use a barra de endereço ou os atalhos (ex.: Bacen) para navegar.

![Navegador no Bacen](images/usage-browser-bacen.jpg)

### 5.2 Computadores

![Painel de computadores](images/portal-sessions.jpg)

1. Clique em **Computadores** ou no botão **Abrir Computadores** no Início.
2. Escolha o desktop ou aplicação liberado ao seu perfil.
3. A sessão abre **dentro do SegPortal** (mesma aba). Use **Fechar sessão** para encerrar.
4. Computadores extras aparecem somente após aprovação do administrador.

Pedido de computador (exemplo):

```bash
./scripts/request-connection.sh usuario "Desktop Financeiro" rdp 10.10.20.51 3389 "Justificativa"
```

Detalhes: [CONNECTIONS.md](CONNECTIONS.md).

---

## 6. Boas práticas e segurança

- Encerre a sessão e use **Sair** ao terminar o expediente.
- Não compartilhe senha nem deixe a sessão aberta em computador público.
- Prefira o **Navegador Web SegPortal** para sites que exigem IP institucional.
- Em dúvida sobre permissão de pasta, fale com o suporte/Nuvem AQNE.

---

## 7. Problemas comuns

| Sintoma | O que tentar |
|---------|----------------|
| Login inválido | Confira Caps Lock; no demo use `usuario`/`usuario` |
| Nenhuma pasta AD | Marque Active Directory no login; peça liberação ao admin |
| Montar nuvem não abre OAuth | Ambiente em modo demo — esperado sem `client_id` |
| Não envia arquivo | Pasta pode ser somente leitura ou arquivo acima do limite |
| SegPortal / Computadores não abre | Confirme o serviço do portal em `:8090` e as abas **Navegador** / **Computadores** |

---

## 8. Imagens deste manual

| Arquivo | Conteúdo |
|---------|----------|
| [usage-login.jpg](images/usage-login.jpg) | Login |
| [portal-home-ad.jpg](images/portal-home-ad.jpg) | Dashboard com AD |
| [portal-cloud-mounted.jpg](images/portal-cloud-mounted.jpg) | OneDrive/Google Drive |
| [portal-files.jpg](images/portal-files.jpg) | Gerenciador |
| [portal-files-folder.jpg](images/portal-files-folder.jpg) | Nova pasta |
| [portal-sessions.jpg](images/portal-sessions.jpg) | Aba Computadores |
| [usage-browser.jpg](images/usage-browser.jpg) | Aba Navegador |
| [usage-browser-bacen.jpg](images/usage-browser-bacen.jpg) | Navegador no Bacen |
| [usage-session.jpg](images/usage-session.jpg) | Sessão de computador |
