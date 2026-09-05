# Contribuindo — SegPortal TJSE

Obrigado por contribuir com o portal ZTNA do Tribunal de Justiça de Sergipe.

## Pré-requisitos

- Docker e Docker Compose
- Python 3.11+
- `kubectl` (para validação K8s)
- Acesso à rede TJSE para testes LDAP (opcional em dev)

## Configuração local

```bash
cp .env.example .env
# Edite credenciais locais
pip install -r requirements-dev.txt
docker compose up -d
```

Portal: http://localhost:8080/guacamole

## Fluxo de trabalho

1. Crie um branch a partir de `develop`: `feature/minha-mudanca`
2. Faça commits descritivos em português ou inglês técnico
3. Execute `pytest` e `./scripts/validate-k8s.sh`
4. Abra PR para `develop` usando o template
5. Após aprovação, merge para `develop` → deploy staging automático
6. Releases de produção via tag `v*.*.*` na `main`

## Padrões de código

- Python: `ruff` (config em `pyproject.toml`)
- Shell: `set -euo pipefail`, scripts em `scripts/`
- Kubernetes: Kustomize overlays, sem secrets reais no repositório
- Docker: Guacamole **sempre** com build context na raiz do repositório

## Segredos

Nunca commite:

- Senhas LDAP, RADIUS ou PostgreSQL
- Certificados privados (`.pem`, `.key`)
- Arquivos `.env` (exceto `.env.example`)

Use `k8s/**/secret.example.yaml` como referência e aplique Secrets no cluster.

## Documentação

Atualize os documentos em `docs/` quando alterar arquitetura, configuração ou deploy.

## Contato

Área de TI / Segurança da Informação — TJSE
