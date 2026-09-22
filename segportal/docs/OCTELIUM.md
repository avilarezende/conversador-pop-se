# ZTNA com Octelium — SegPortal

O acesso externo deixa de ser um Ingress/VPN aberto e passa pelo [Octelium](https://octelium.com/docs/octelium/latest/overview/intro): proxy com identidade, política por requisição e modo clientless (BeyondCorp) para o portal.

Este diretório no monorepo é o recorte do SegPortal preparado para esse modelo. Um fork GitHub de `avilarezende/segportal` não foi criado daqui (o token deste agente não tem permissão de escrita nesse repositório).

## O que fica público

| Service Octelium | Modo | Quem entra | Upstream (namespace `segportal`) |
|------------------|------|------------|----------------------------------|
| `portal` | `WEB`, `isPublic: true` | humanos `@aqne.jus.br` | `portal-auth:8090` |
| `sessoes` | `HTTP` (só cliente) | grupo `admins` | `guacamole:8080` |

URL pública do portal: `https://portal.<OCTELIUM_DOMAIN>`.

Guacamole, VNC, Postgres e o proxy de egress **não** são publicados na internet. O usuário usa o navegador HTML5 pelo portal; o admin alcança `sessoes` depois de `octelium connect`.

## Instalação do Cluster

Em uma VM Linux (Ubuntu 24.04+, 2 GB RAM, 20 GB disco), como root, com um domínio seu:

```bash
curl -o install-cluster.sh https://octelium.com/install-cluster.sh
chmod +x install-cluster.sh
./install-cluster.sh --domain <DOMINIO>
```

Guia: https://octelium.com/docs/octelium/latest/overview/quick-install

CLI de gestão:

```bash
curl -fsSL https://octelium.com/install.sh | bash
export OCTELIUM_DOMAIN=<DOMINIO>
./octelium/scripts/apply.sh
```

Antes disso, o SegPortal precisa estar no mesmo Kubernetes (ou alcançável pelo Cluster) com o Service `portal-auth`.

## Identidade

O exemplo OIDC está em `octelium/examples/identityprovider.example.yaml`. O callback do IdP é `https://<OCTELIUM_DOMAIN>/callback`. O client secret entra só como Secret do Octelium (`octeliumctl create secret`), nunca no Git.

Usuários de exemplo: `octelium/examples/users.example.yaml`.

## Compose local

O arquivo `docker-compose.octelium.yml` prende as portas 8080 e 8090 a `127.0.0.1`, para a borda pública ser o Octelium:

```bash
docker compose -f docker-compose.yml -f docker-compose.octelium.yml up -d
```

## Manifestos

```
octelium/cluster/policies.yaml    # segportal-usuarios, segportal-admins
octelium/cluster/groups.yaml
octelium/cluster/services.yaml    # portal + sessoes
```
