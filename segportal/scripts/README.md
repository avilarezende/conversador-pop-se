# Scripts — SegPortal TJSE

Utilitários de inicialização e validação do projeto.

| Script | Descrição |
|--------|-----------|
| [bootstrap-segportal.sh](bootstrap-segportal.sh) | **Padrão no boot** — schema + papéis + navegador HTML + pedidos |
| [init-db.sh](init-db.sh) | Só schema PostgreSQL do Guacamole 1.5.5 (legado/manual) |
| [init-db-dev.sh](init-db-dev.sh) | Schema + admin para uso manual |
| [seed-roles.sh](seed-roles.sh) | Só papéis admin/usuário |
| [seed-browser-and-requests.sh](seed-browser-and-requests.sh) | Atalho → chama `bootstrap-segportal.sh` |
| [request-connection.sh](request-connection.sh) | Usuário solicita terminal/aplicação |
| [approve-connection-request.sh](approve-connection-request.sh) | Admin aprova/rejeita pedido |
| [change-local-password.sh](change-local-password.sh) | Altera senha de usuário local (ex.: guacadmin) |
| [delete-local-user.sh](delete-local-user.sh) | Desativa ou exclui usuário local |
| [validate-k8s.sh](validate-k8s.sh) | Valida overlays Kustomize (dev/staging/prod) |

## Uso

O compose sobe `segportal-bootstrap` sozinho. Reexecução manual:

```bash
export POSTGRES_PASSWORD=...
./scripts/bootstrap-segportal.sh

# Admin padrão
./scripts/change-local-password.sh guacadmin 'NovaSenhaForte!'
./scripts/validate-k8s.sh
```
