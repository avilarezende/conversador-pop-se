# Deploy — SegPortal TJSE

Guia de implantação em Docker Compose (dev) e Kubernetes/Rancher (produção).

## Desenvolvimento local

```bash
git clone https://github.com/avilarezende/segportal.git
cd segportal
cp .env.example .env
# Configure POSTGRES_PASSWORD e credenciais LDAP (se disponíveis)
docker compose up -d --build
```

Acesse: http://localhost:8080/guacamole

Inicialize o schema (primeira execução):

```bash
docker compose exec postgres bash -c 'POSTGRES_HOSTNAME=localhost ./scripts/init-db.sh'
```

## Kubernetes

### Pré-requisitos

- Cluster Rancher 2.x com Ingress NGINX
- cert-manager para TLS
- Registry: `registry.tjse.jus.br/segportal`

### Secrets

Crie secrets a partir dos exemplos antes do deploy:

```bash
kubectl create namespace segportal
kubectl apply -f k8s/postgres/secret.example.yaml -n segportal  # substitua valores
kubectl apply -f k8s/guacamole/secret.example.yaml -n segportal
```

### Overlays

| Overlay | Uso | Comando |
|---------|-----|---------|
| `development` | Lab interno | `kubectl apply -k k8s/overlays/development` |
| `staging` | Homologação | `kubectl apply -k k8s/overlays/staging` |
| `production` | Produção | `kubectl apply -k k8s/overlays/production` |

### Validação

```bash
./scripts/validate-k8s.sh
```

## Rancher Fleet (GitOps)

1. Aplique `k8s/rancher-fleet/gitrepo.yaml` no cluster Fleet
2. O path `k8s/overlays/production` é sincronizado automaticamente
3. Clusters alvo: label `env=production`

Configuração adicional em `k8s/rancher-fleet/fleet.yaml`.

## CI/CD

| Pipeline | Trigger | Ação |
|----------|---------|------|
| `ci.yml` | PR / push | Testes, lint, build Docker, validate K8s |
| `cd.yml` | Tag `v*.*.*` | Push imagens + deploy produção |

Detalhes: [CI_CD.md](CI_CD.md)

## Imagens

| Imagem | Dockerfile |
|--------|------------|
| `guacamole` | `services/guacamole/Dockerfile` |
| `guacd` | `services/guacd/Dockerfile` |
| `egress-proxy` | `services/egress-proxy/Dockerfile` |

Todas constroem com `context: .` (raiz do repo).

## Rollback

```bash
kubectl rollout undo deployment/guacamole -n segportal
kubectl rollout undo deployment/guacd -n segportal
```

## Monitoramento

- Health checks HTTP/TCP em todos os Deployments
- Logs: `kubectl logs -l app.kubernetes.io/name=guacamole -n segportal`
- Métricas HPA: CPU 65–70% target
