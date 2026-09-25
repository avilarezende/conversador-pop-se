# SegPortal + Octelium (ZTNA)

Fork operacional do SegPortal em que a fronteira **Zero Trust** deixa de ser o Ingress público e passa a ser um [Cluster Octelium](https://octelium.com/docs/octelium/latest/overview/quick-install).

O Guacamole, o portal-auth, RDP e SSH continuam como aplicações. Eles ficam em endereços **privados**. Quem chega até eles é o Octelium, depois de autenticar a identidade e avaliar a Policy.

```
Usuário (navegador ou octelium connect)
        │  identidade (OIDC/SAML/AD) + Policy por requisição
        ▼
Cluster Octelium  (namespace Kubernetes `octelium`)
        │  HTTP público: segportal, portal-auth
        │  TCP/SSH: desktops e jump host (só via connect)
        ▼
Namespace `segportal`  (NetworkPolicy: sem Ingress público)
```

## O que este fork publica

| Serviço Octelium | Modo | Quem acessa | Upstream privado |
|------------------|------|-------------|------------------|
| `segportal` | HTTP público | `segportal-users` e `segportal-admins` | `guacamole.segportal.svc:8080` |
| `portal-auth` | HTTP público | mesmos grupos | `portal-auth.segportal.svc:8090` |
| `desktop-financeiro` | TCP 3389 | mesmos grupos | `tcp://10.10.20.51:3389` |
| `desktop-admin` | TCP 3389 | só `segportal-admins` | `tcp://10.10.20.10:3389` |
| `jump-ssh` | SSH | só `segportal-admins` | `ssh://10.10.20.10:22` |

Arquivos: [`cluster/`](cluster/).

Usuários demo (substitua por IdentityProvider em produção):

| Usuário | Grupos |
|---------|--------|
| `admin` | `segportal-admins`, `segportal-users` (Policy `allow-all` do Cluster) |
| `usuario` | `segportal-users` |

## Instalar o Cluster

Um nó Linux (2 GB RAM, 20 GB de disco) e um domínio:

```bash
curl -o install-cluster.sh https://octelium.com/install-cluster.sh
chmod +x install-cluster.sh
./install-cluster.sh --domain segportal.exemplo.jus.br
```

Para um cluster Kubernetes que já existe, use [`octops init`](https://octelium.com/docs/octelium/latest/install/cluster/installing-cluster). O namespace da aplicação SegPortal e o namespace `octelium` precisam se alcançar na rede do cluster.

CLI:

```bash
curl -fsSL https://octelium.com/install.sh | bash
octelium login
```

## Aplicar o ZTNA do SegPortal

```bash
chmod +x octelium/scripts/apply.sh
./octelium/scripts/apply.sh
```

Sem `octeliumctl`, o script só valida o YAML.

## Subir a aplicação sem Ingress público

```bash
kubectl apply -k k8s/overlays/octelium
```

Esse overlay remove o Ingress `segportal` e aplica uma NetworkPolicy: só pods do namespace `octelium` e do próprio `segportal` entram nos workloads.

## Como o usuário entra

HTTP (navegador, sem cliente VPN):

- `https://segportal.<domínio-do-cluster>`
- `https://portal-auth.<domínio-do-cluster>`

O portal de autenticação do Octelium pede a identidade antes de encaminhar ao upstream.

TCP e SSH:

```bash
octelium connect -p desktop-financeiro:3389
octelium connect -p jump-ssh:22
ssh -p 22 segportal@127.0.0.1
```

## Identidade corporativa

Não use os usuários demo fora do laboratório. Crie um IdentityProvider OpenID Connect ou SAML 2.0 apontando para o Active Directory e faça o `email` / `identifier` do User coincidir com a conta. Referência: [Users](https://octelium.com/docs/octelium/latest/management/core/user).

Hosts RDP/SSH atrás de NAT podem ser publicados por um cliente `octelium connect --serve` em vez de URL fixa. A host key de `jump-ssh` está ignorada de propósito no laboratório; em produção grave a chave pública do servidor.

## Referências

- [Quick install](https://octelium.com/docs/octelium/latest/overview/quick-install)
- [HTTP Services](https://octelium.com/docs/octelium/latest/management/core/service/http)
- [Policies](https://octelium.com/docs/octelium/latest/management/core/policy)
- [SECURITY.md](../docs/SECURITY.md)
