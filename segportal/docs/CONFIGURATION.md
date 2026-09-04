# Configuração — SegPortal TJSE

Guia passo a passo para configurar LDAP, MFA, Guacamole, proxy de egress e Kubernetes.

---

## Índice

1. [Pré-requisitos](#1-pré-requisitos)
2. [Active Directory (LDAP)](#2-active-directory-ldap)
3. [MFA via RADIUS](#3-mfa-via-radius)
4. [Guacamole e PostgreSQL](#4-guacamole-e-postgresql)
5. [Proxy de egress (Squid)](#5-proxy-de-egress-squid)
6. [Branding TJSE](#6-branding-tjse)
7. [Kubernetes / Rancher](#7-kubernetes--rancher)
8. [Inicialização do banco](#8-inicialização-do-banco)
9. [Cadastro de conexões](#9-cadastro-de-conexões)
10. [Validação pós-configuração](#10-validação-pós-configuração)

---

## 1. Pré-requisitos

Antes de configurar, garanta:

| Item | Requisito |
|------|-----------|
| Rede | Cluster Kubernetes acessa `ldap.tjse.jus.br:636` e `radius.tjse.jus.br:1812` |
| AD | Conta de serviço com permissão de leitura em usuários e grupos |
| DNS | `segportal.tjse.jus.br` apontando para o Ingress |
| TLS | Certificado válido para o hostname do portal |
| Registry | Imagens publicadas em `registry.tjse.jus.br/segportal` (ou ajustar overlays) |

---

## 2. Active Directory (LDAP)

### 2.1 Criar conta de serviço no AD

Crie uma conta dedicada, por exemplo:

```
CN=svc-segportal,OU=Servicos,DC=tjse,DC=jus,DC=br
```

Permissões mínimas:
- Leitura em `OU=Usuarios,DC=tjse,DC=jus,DC=br`
- Leitura em `OU=Grupos,DC=tjse,DC=jus,DC=br`

### 2.2 Variáveis de ambiente

Copie `.env.example` para `.env` e preencha:

```bash
LDAP_HOSTNAME=ldap.tjse.jus.br
LDAP_PORT=636
LDAP_ENCRYPTION_METHOD=ssl
LDAP_USER_BASE_DN=OU=Usuarios,DC=tjse,DC=jus,DC=br
LDAP_USERNAME_ATTRIBUTE=sAMAccountName
LDAP_SEARCH_BIND_DN=CN=svc-segportal,OU=Servicos,DC=tjse,DC=jus,DC=br
LDAP_SEARCH_BIND_PASSWORD=<senha_da_conta_servico>
```

### 2.3 Arquivo de referência

O mapeamento LDAP está em `config/ldap/ldap.properties`. O `entrypoint.sh` do Guacamole renderiza este arquivo com `envsubst` na inicialização do container.

### 2.4 Grupos AD → papéis e recursos SegPortal

| Grupo AD | Papel | Recursos |
|----------|-------|----------|
| `GG-SegPortal-Admin` | **Administrador** | Gestão completa + visão de sessões |
| `GG-SegPortal-Usuarios` | **Usuário** | Base de acesso (sem admin) |
| `GG-SegPortal-Financeiro` | Negócio | RDP — estações financeiro |
| `GG-SegPortal-Consulta` | Negócio | VNC — terminais de consulta |
| `GG-SegPortal-Externo` | Negócio | Proxy egress (IP TJSE) |

Documento dedicado: **[ROLES.md](ROLES.md)** · definição em `config/roles/roles.yaml`.

**Passos no Guacamole (após primeiro login admin):**

1. Acesse **Settings → Groups**
2. Crie grupos com os mesmos nomes dos grupos AD (`segportal-admins`, `segportal-users`, etc.)
3. No grupo admin, conceda permissões de sistema (`ADMINISTER`, `CREATE_*`)
4. Em **Settings → Connections**, associe cada conexão ao grupo de negócio com permissão `READ`
5. Usuários normais **não** recebem permissões de sistema

Seed automático (demo JDBC):

```bash
./scripts/seed-roles.sh
# ou: psql ... < scripts/sql/003-segportal-roles.sql
```

---

## 3. MFA via RADIUS

### 3.1 Habilitar MFA

```bash
MFA_ENABLED=true
MFA_RADIUS_HOST=radius.tjse.jus.br
MFA_RADIUS_PORT=1812
MFA_RADIUS_SECRET=<shared_secret_do_radius>
```

### 3.2 Como funciona

1. Usuário informa login e senha AD no portal.
2. Guacamole valida credenciais no LDAP.
3. Em seguida, envia `Access-Request` ao servidor RADIUS corporativo.
4. O RADIUS valida o segundo fator (TOTP, token hardware ou push).
5. Somente com `Access-Accept` a sessão é liberada.

### 3.3 Teste do RADIUS

```bash
# Exemplo com radclient (instalar freeradius-utils)
echo "User-Name=joao.silva,User-Password=senha,OTP=123456" | \
  radclient -x radius.tjse.jus.br:1812 auth <shared_secret>
```

---

## 4. Guacamole e PostgreSQL

### 4.1 Variáveis principais

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `POSTGRES_DB` | Nome do banco | `guacamole_db` |
| `POSTGRES_USER` | Usuário PostgreSQL | `guacamole_user` |
| `POSTGRES_PASSWORD` | Senha do banco | *(obrigatório)* |
| `GUACAMOLE_HOSTNAME` | Hostname público | `segportal.tjse.jus.br` |
| `SESSION_TIMEOUT_MINUTES` | Timeout inatividade | `60` |

### 4.2 Arquivo `config/guacamole/guacamole.properties`

Principais chaves (renderizadas pelo entrypoint):

```properties
guacd-hostname: guacd
guacd-port: 4822
postgresql-hostname: postgres
postgresql-database: guacamole_db
api-session-timeout: 60
user-session-timeout: 60
```

### 4.3 Imagem Docker

O `services/guacamole/Dockerfile`:

- Base: `guacamole/guacamole:1.5.5`
- Extensão LDAP: `guacamole-auth-ldap-1.5.5.jar`
- **Build a partir da raiz do repositório:**

```bash
docker build -f services/guacamole/Dockerfile -t segportal/guacamole:latest .
```

---

## 5. Proxy de egress (Squid)

O proxy permite que usuários autorizados acessem sites externos **com o IP institucional do TJSE**, sem VPN.

### 5.1 Configuração

Arquivo: `config/proxy/squid.conf` (copiado para `services/egress-proxy/squid.conf` na imagem).

Domínios liberados por padrão:
- `.tjse.jus.br`
- `.jus.br`
- `.gov.br`
- `.pje.jus.br`

### 5.2 Adicionar novo domínio

Edite `config/proxy/squid.conf`:

```squid
acl novo_dominio dstdomain .exemplo.gov.br
http_access allow novo_dominio
```

Reconstrua e redeploy o pod `proxy-egress`.

### 5.3 Variáveis

```bash
EGRESS_PROXY_HOST=proxy-egress
EGRESS_PROXY_PORT=3128
```

---

## 6. Branding TJSE

Arquivos em `services/guacamole/branding/`:

| Arquivo | Função |
|---------|--------|
| `tjse-logo.svg` | Logotipo na tela de login |
| `guac-login.css` | Cores institucionais (#003366, #c9a227) |
| `translations/pt.json` | Textos em português |

Substitua `tjse-logo.svg` pelo logotipo oficial do tribunal antes de produção.

---

## 7. Kubernetes / Rancher

### 7.1 Criar namespace e secrets

```bash
kubectl create namespace segportal

kubectl -n segportal create secret generic segportal-secrets \
  --from-literal=POSTGRES_PASSWORD='SUA_SENHA' \
  --from-literal=LDAP_SEARCH_BIND_PASSWORD='SENHA_LDAP' \
  --from-literal=MFA_RADIUS_SECRET='SECRET_RADIUS'
```

Ou copie e preencha os exemplos:
- `k8s/postgres/secret.example.yaml`
- `k8s/guacamole/secret.example.yaml`

### 7.2 Overlays por ambiente

| Overlay | Hostname | Uso |
|---------|----------|-----|
| `development` | `segportal-dev.tjse.jus.br` | Desenvolvimento |
| `staging` | `segportal-stg.tjse.jus.br` | Homologação |
| `production` | `segportal.tjse.jus.br` | Produção |

```bash
# Homologação
kubectl apply -k k8s/overlays/staging

# Produção
kubectl apply -k k8s/overlays/production
```

### 7.3 GitOps (Rancher Fleet)

O arquivo `k8s/rancher-fleet/fleet.yaml` sincroniza automaticamente o overlay de produção nos clusters com label `env=production`.

### 7.4 Escalonamento (HPA)

| Pod | Mínimo | Máximo | Métrica |
|-----|--------|--------|---------|
| guacamole | 2 | 10 | CPU 70% |
| guacd | 2 | 20 | CPU 60% |
| proxy-egress | 1 | 5 | CPU 75% |

---

## 8. Inicialização do banco

Execute **uma vez** após o PostgreSQL estar disponível:

```bash
export POSTGRES_PASSWORD=<senha>
export POSTGRES_HOST=postgres   # ou localhost em dev
./scripts/init-db.sh
```

O script aplica o schema oficial Guacamole 1.5.5 para PostgreSQL.

**Usuário admin padrão** (altere imediatamente após primeiro acesso):
- Usuário: `guacadmin`
- Senha: `guacadmin`

---

## 9. Cadastro de conexões

### 9.1 Via interface web

1. Login como admin em `/guacamole`
2. **Settings → Connections → New Connection**
3. Preencha protocolo (RDP/VNC/SSH), host, porta e credenciais
4. Associe ao grupo AD correspondente

### 9.2 Exemplo de conexão RDP

| Campo | Valor exemplo |
|-------|---------------|
| Nome | Estação Financeiro |
| Protocolo | RDP |
| Hostname | `10.10.20.50` |
| Porta | `3389` |
| Grupo | `GG-SegPortal-Financeiro` |

---

## 10. Validação pós-configuração

### Checklist

- [ ] Login LDAP com usuário de teste funciona
- [ ] MFA é solicitado e aceito
- [ ] Conexão RDP/VNC abre no navegador
- [ ] Proxy egress responde na porta 3128
- [ ] Timeout de sessão respeitado após inatividade
- [ ] Usuário sem grupo AD não vê recursos indevidos
- [ ] Certificado TLS válido no Ingress
- [ ] Logs sem erros de bind LDAP

### Comandos de verificação

```bash
# Testes automatizados
pip install -r requirements-dev.txt
pytest tests -v

# Validar manifests K8s
./scripts/validate-k8s.sh

# Status dos pods
kubectl -n segportal get pods,svc,ingress,hpa
```

---

## Referências

- [MANUAL.md](MANUAL.md) — manual do usuário e administrador
- [DEPLOYMENT.md](DEPLOYMENT.md) — deploy detalhado no Rancher
- [SECURITY.md](SECURITY.md) — controles de segurança
