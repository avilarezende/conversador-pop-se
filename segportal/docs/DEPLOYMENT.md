# Deploy — SegPortal AQNE

Guia de implantação em Docker Compose (dev) e Kubernetes/Rancher (produção).

## Desenvolvimento local

```bash
git clone https://github.com/avilarezende/segportal.git
cd segportal
cp .env.example .env
# Configure POSTGRES_PASSWORD (LDAP/MFA opcionais)
docker compose up --build
```

Acesse: http://localhost:8090

O serviço **`segportal-bootstrap`** aplica schema (se necessário), papéis e a conexão **Navegador Web SegPortal** automaticamente. O serviço **`web-browser`** (Firefox/VNC) sobe junto ao stack.

Demo sem LDAP:

```bash
docker compose -f docker-compose.dev.yml up --build
# admin / admin  ·  usuario / usuario
```

Reaplicar bootstrap (idempotente):

```bash
./scripts/bootstrap-segportal.sh
```

## Kubernetes

### Pré-requisitos

- Cluster Rancher 2.x com Ingress NGINX
- cert-manager para TLS
- Registry: `registry.aqne.jus.br/segportal`

### Secrets

```bash
kubectl create namespace segportal
kubectl apply -f k8s/postgres/secret.example.yaml -n segportal  # substitua valores
kubectl apply -f k8s/secret.example.yaml -n segportal
```

### Overlays

| Overlay | Uso | Comando |
|---------|-----|---------|
| `development` | Lab interno | `kubectl apply -k k8s/overlays/development` |
| `staging` | Homologação | `kubectl apply -k k8s/overlays/staging` |
| `production` | Produção | `kubectl apply -k k8s/overlays/production` |

O Job **`segportal-bootstrap`** (`k8s/bootstrap`) roda no apply e habilita o navegador padrão.

### Validação

```bash
./scripts/validate-k8s.sh
kubectl -n segportal get pods,job
kubectl -n segportal logs job/segportal-bootstrap
```

![Pods](images/k8s-pods.jpg)

## Rancher Fleet (GitOps)

1. Aplique `k8s/rancher-fleet/gitrepo.yaml` no cluster Fleet
2. O path `k8s/overlays/production` é sincronizado automaticamente
3. Clusters alvo: label `env=production`

## CI/CD

| Pipeline | Trigger | Ação |
|----------|---------|------|
| `ci.yml` | PR / push | Testes, lint, build Docker, validate K8s |
| `cd.yml` | Tag `v*.*.*` | Push imagens + deploy produção |

Detalhes: [CI_CD.md](CI_CD.md)

## Imagens Docker

| Imagem | Dockerfile |
|--------|------------|
| `sessões` | `services/Dockerfile` |
| `guacd` | `services/guacd/Dockerfile` |
| `egress-proxy` | `services/egress-proxy/Dockerfile` |
| `web-browser` | `services/web-browser/Dockerfile` |

## Rollback

```bash
kubectl rollout undo deployment -n segportal
kubectl rollout undo deployment/guacd -n segportal
kubectl rollout undo deployment/web-browser -n segportal
```

## Monitoramento

- Probes HTTP/TCP nos Deployments (`web-browser` na porta 5900)
- Logs: `kubectl logs -l app=sessions -n segportal`
- Bootstrap: `kubectl logs job/segportal-bootstrap -n segportal`

## Referências

- [CONFIGURATION.md](CONFIGURATION.md)
- [CONNECTIONS.md](CONNECTIONS.md)
- [MANUAL.md](MANUAL.md)
