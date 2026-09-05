# Arquivos e nuvem — SegPortal

O **portal-auth** (porta **8090**) oferece o dashboard pessoal com:

1. **Compartilhamentos Active Directory** — home (`homeDirectory` / `homeDrive`), pastas departamentais e públicos indicados pelo AD
2. **OneDrive e Google Drive** — montagem opcional no dashboard principal
3. **Gerenciador HTML** — listar, enviar (arrastar e soltar), criar pasta, renomear, baixar e excluir

## Fluxo com Active Directory

1. Usuário marca **Autenticar via Active Directory** (ou `LDAP_ENABLED=true`)
2. O portal resolve shares em [`config/files/shares.yaml`](../config/files/shares.yaml) (`shares.ad_attributes` + `shares.corporate`)
3. Em produção, o caminho UNC do `homeDirectory` é montado no backend de arquivos; em demo, usa árvore local em `DEMO_SHARES_ROOT`

## Configuração

```yaml
cloud_drives:
  onedrive:
    enabled: true
    client_id: ""   # vazio = modo demo
  google_drive:
    enabled: true
    client_id: ""
```

## API (resumo)

| Método | Rota | Uso |
|--------|------|-----|
| POST | `/api/login` | Sessão cookie (`use_active_directory`) |
| GET | `/api/dashboard` | Shares AD + estado das nuvens |
| GET | `/api/files/{share_id}` | Listar pasta |
| POST | `/api/files/{share_id}/upload` | Enviar arquivo |
| POST | `/api/cloud/{provider}/mount` | Montar OneDrive / Google Drive |

## UI

Interface em HTML/CSS/JS (`services/portal-auth/static`), tipografia Source Sans 3 + Fraunces,
cores institucionais TJSE (navy / ouro), navegação por abas Início · Arquivos · Sessões,
diálogo acessível para nova pasta/renomear, arrastar e soltar, e alvos de clique ≥ 44px.

Documentação relacionada: [USAGE.md](USAGE.md), [CONNECTIONS.md](CONNECTIONS.md), [ROLES.md](ROLES.md).
