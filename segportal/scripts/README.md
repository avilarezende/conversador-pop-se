# Scripts — SegPortal TJSE

Utilitários de inicialização e validação do projeto.

| Script | Descrição |
|--------|-----------|
| [init-db.sh](init-db.sh) | Aplica schema PostgreSQL do Guacamole 1.5.5 |
| [validate-k8s.sh](validate-k8s.sh) | Valida overlays Kustomize (dev/staging/prod) |

## Uso

```bash
# Inicializar banco (requer psql e acesso ao PostgreSQL)
export POSTGRES_PASSWORD=...
./scripts/init-db.sh

# Validar manifests Kubernetes
./scripts/validate-k8s.sh
```

O `init-db.sh` também é montado no container PostgreSQL do `docker-compose.yml` para bootstrap local.
