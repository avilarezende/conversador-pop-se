# Configuração — SegPortal TJSE

Guia passo a passo: usuários locais, admin padrão, LDAP opcional, MFA, proxy e Kubernetes.

---

## Índice

1. [Pré-requisitos](#1-pré-requisitos)
2. [Admin padrão e usuários locais](#2-admin-padrão-e-usuários-locais)
3. [Active Directory (LDAP) — opcional](#3-active-directory-ldap--opcional)
4. [MFA via RADIUS](#4-mfa-via-radius)
5. [Guacamole e PostgreSQL](#5-guacamole-e-postgresql)
6. [Proxy de egress (Squid)](#6-proxy-de-egress-squid)
7. [Branding TJSE](#7-branding-tjse)
8. [Kubernetes / Rancher](#8-kubernetes--rancher)
9. [Inicialização do banco](#9-inicialização-do-banco)
10. [Cadastro de conexões](#10-cadastro-de-conexões)
11. [Validação pós-configuração](#11-validação-pós-configuração)

---

## 1. Pré-requisitos

| Item | Requisito |
|------|-----------|
| Docker / Kubernetes | Ambiente para subir os pods |
| DNS / TLS | `segportal.tjse.jus.br` (produção) |
| LDAP (opcional) | AD acessível + conta de serviço + cadeia CA |
| RADIUS (opcional) | MFA corporativo |

**LDAP não é obrigatório.** Sem ele, o portal funciona com usuários locais e o admin padrão.

---

## 2. Admin padrão e usuários locais

Documento completo: **[LOCAL_ADMIN.md](LOCAL_ADMIN.md)**

| Campo | Valor |
|-------|-------|
| Usuário | `guacadmin` |
| Senha inicial | `guacadmin` |
| Depende de LDAP? | **Não** |

### Alterar senha

```bash
./scripts/change-local-password.sh guacadmin 'NovaSenhaForte!'
```

Ou pela UI: login → Preferences → alterar senha.

### Desativar / excluir

```bash
./scripts/delete-local-user.sh guacadmin --disable   # recomendado
./scripts/delete-local-user.sh guacadmin --delete    # permanente
```

Só exclua depois de criar outro administrador.

### Gerenciar usuários locais (sem LDAP)

1. Login como `guacadmin`
2. **Settings → Users → New User**
3. Defina senha e permissões / grupos

Com `LDAP_ENABLED=false` (padrão), essa é a única forma de autenticação.

---

## 3. Active Directory (LDAP) — opcional

O administrador configura os apontamentos LDAP. Referência editável:

- `config/ldap/ldap-settings.yaml`
- Variáveis em `.env` / ConfigMap / Secret

### 3.1 Campos configuráveis

| Campo | Variável | Descrição |
|-------|----------|-----------|
| Liga LDAP | `LDAP_ENABLED` | `true` / `false` (padrão `false`) |
| Servidor | `LDAP_HOSTNAME` | Ex.: `ldap.tjse.jus.br` |
| Porta | `LDAP_PORT` | `636` (LDAPS) ou `389` |
| Criptografia | `LDAP_ENCRYPTION_METHOD` | `ssl`, `starttls` ou `none` |
| Domínio | `ldap.domain` em yaml | `tjse.jus.br` |
| Base usuários | `LDAP_USER_BASE_DN` | `OU=Usuarios,DC=tjse,DC=jus,DC=br` |
| Base grupos | `LDAP_GROUP_BASE_DN` | `OU=Grupos,DC=tjse,DC=jus,DC=br` |
| UID / atributo | `LDAP_USERNAME_ATTRIBUTE` | `sAMAccountName`, `uid`, `cn`, `userPrincipalName` |
| Filtro usuário | `LDAP_USER_SEARCH_FILTER` | `(objectClass=user)` |
| Filtro grupo | `LDAP_GROUP_SEARCH_FILTER` | `(objectClass=group)` |
| Atributo membro | `LDAP_MEMBER_ATTRIBUTE` | `member` |
| Bind DN | `LDAP_SEARCH_BIND_DN` | Conta de serviço |
| Senha bind | `LDAP_SEARCH_BIND_PASSWORD` | **Secret** |
| Cadeia CA | `LDAP_CA_CHAIN_FILE` | PEM em `/etc/guacamole/certs/` |
| Cert. servidor | `LDAP_SERVER_CERTIFICATE_FILE` | Opcional |
| Truststore | `LDAP_TRUSTSTORE_FILE` | Gerado pelo entrypoint |

### 3.2 Procedimento do administrador

1. Coloque a cadeia CA em `config/ldap/certs/ldap-ca-chain.pem`
2. Preencha `.env` (ou Secret Rancher) com servidor, porta, domain/DN, uid, bind
3. Defina `LDAP_ENABLED=true`
4. Reinicie o Guacamole: `kubectl -n segportal rollout restart deployment/guacamole`
5. Teste login AD **mantendo** o `guacadmin` local

Se `LDAP_ENABLED=false`, o `entrypoint.sh` remove todas as chaves `ldap-*` e o portal fica só com JDBC.

### 3.3 Conta de serviço no AD

```
CN=svc-segportal,OU=Servicos,DC=tjse,DC=jus,DC=br
```

Permissões mínimas: leitura em usuários e grupos.

### 3.4 Grupos AD → papéis

| Grupo AD | Papel |
|----------|-------|
| `GG-SegPortal-Admin` | Administrador |
| `GG-SegPortal-Usuarios` | Usuário |
| `GG-SegPortal-Financeiro` / `Consulta` / `Externo` | Negócio |

Ver [ROLES.md](ROLES.md). Seed: `./scripts/seed-roles.sh`.

---

## 4. MFA via RADIUS

```bash
MFA_ENABLED=true
MFA_RADIUS_HOST=radius.tjse.jus.br
MFA_RADIUS_PORT=1812
MFA_RADIUS_SECRET=<shared_secret>
```

Recomendado somente com LDAP habilitado. Com `MFA_ENABLED=false`, o entrypoint remove as chaves `radius-*`.

---

## 5. Guacamole e PostgreSQL

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `POSTGRES_DB` | Banco | `guacamole_db` |
| `POSTGRES_USER` | Usuário | `guacamole_user` |
| `POSTGRES_PASSWORD` | Senha | *(obrigatório)* |
| `SESSION_TIMEOUT_MINUTES` | Timeout | `60` |

Build da imagem:

```bash
docker build -f services/guacamole/Dockerfile -t segportal/guacamole:latest .
```

---

## 6. Proxy de egress (Squid)

Arquivo: `config/proxy/squid.conf` / `services/egress-proxy/squid.conf`.

---

## 7. Branding TJSE

Arquivos em `services/guacamole/branding/`.

---

## 8. Kubernetes / Rancher

```bash
kubectl create namespace segportal
kubectl -n segportal create secret generic segportal-secrets \
  --from-literal=POSTGRES_PASSWORD='...' \
  --from-literal=LDAP_SEARCH_BIND_PASSWORD='...' \
  --from-literal=MFA_RADIUS_SECRET='...'
kubectl apply -k k8s/overlays/production
```

ConfigMap `segportal-common` traz `LDAP_ENABLED=false` por padrão. Para ligar LDAP, edite o ConfigMap/Secret e monte o volume de certificados CA.

---

## 9. Inicialização do banco

```bash
export POSTGRES_PASSWORD=...
./scripts/init-db.sh
./scripts/seed-roles.sh
```

Cria schema + `guacadmin` + papéis/grupos.

---

## 10. Cadastro de conexões

Login admin → **Settings → Connections → New Connection** → associe ao grupo de negócio.

---

## 11. Validação pós-configuração

- [ ] Login `guacadmin` funciona **sem** LDAP
- [ ] Senha do admin alterada
- [ ] (Se LDAP) login AD + cadeia CA válida
- [ ] Usuário normal vê só o próprio contexto
- [ ] Admin vê sessões / Settings

```bash
pytest tests -v
./scripts/validate-k8s.sh
```

## Referências

- [LOCAL_ADMIN.md](LOCAL_ADMIN.md) — senha e exclusão do admin padrão
- [ROLES.md](ROLES.md) — papéis
- [SECURITY.md](SECURITY.md)
