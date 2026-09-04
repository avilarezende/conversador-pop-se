# Scripts — SegPortal TJSE

Utilitários de inicialização e validação do projeto.

| Script | Descrição |
|--------|-----------|
| [init-db.sh](init-db.sh) | Aplica schema PostgreSQL do Guacamole 1.5.5 |
| [init-db-dev.sh](init-db-dev.sh) | Schema + admin para stack `docker-compose.dev.yml` |
| [seed-roles.sh](seed-roles.sh) | Cria papéis admin/usuário e grupos de negócio |
| [seed-browser-and-requests.sh](seed-browser-and-requests.sh) | Navegador padrão + tabela de pedidos |
| [request-connection.sh](request-connection.sh) | Usuário solicita terminal/aplicação |
| [approve-connection-request.sh](approve-connection-request.sh) | Admin aprova/rejeita pedido |
| [change-local-password.sh](change-local-password.sh) | Altera senha de usuário local (ex.: guacadmin) |
| [delete-local-user.sh](delete-local-user.sh) | Desativa ou exclui usuário local |
| [validate-k8s.sh](validate-k8s.sh) | Valida overlays Kustomize (dev/staging/prod) |

## Uso

```bash
export POSTGRES_PASSWORD=...
./scripts/init-db.sh
./scripts/seed-roles.sh

# Admin padrão
./scripts/change-local-password.sh guacadmin 'NovaSenhaForte!'
./scripts/delete-local-user.sh guacadmin --disable

./scripts/validate-k8s.sh
```

O `init-db.sh` também é montado no container PostgreSQL do `docker-compose.yml` para bootstrap local.
