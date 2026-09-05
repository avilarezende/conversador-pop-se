# Configuração — SegPortal AQNE

Guia passo a passo: usuários locais, admin padrão, LDAP opcional, MFA, proxy, navegador padrão e Kubernetes.

---

## Índice

1. [Pré-requisitos](#1-pré-requisitos)
2. [Admin padrão e usuários locais](#2-admin-padrão-e-usuários-locais)
3. [Active Directory (LDAP) — opcional](#3-active-directory-ldap--opcional)
4. [MFA via RADIUS](#4-mfa-via-radius)
5. [Guacamole e PostgreSQL](#5-guacamole-e-postgresql)
6. [Navegador HTML padrão (automático)](#6-navegador-html-padrão-automático)
7. [Proxy de egress (Squid)](#7-proxy-de-egress-squid)
8. [Branding AQNE](#8-branding-aqne)
9. [Kubernetes / Rancher](#9-kubernetes--rancher)
10. [Pedidos de conexão](#10-pedidos-de-conexão)
11. [Validação pós-configuração](#11-validação-pós-configuração)

---

## 1. Pré-requisitos

| Item | Requisito |
|------|-----------|
| Docker / Kubernetes | Ambiente para subir os pods |
| DNS / TLS | `segportal.aqne.jus.br` (produção) |
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

```bash
./scripts/change-local-password.sh guacadmin 'NovaSenhaForte!'
./scripts/delete-local-user.sh guacadmin --disable
```

Com `LDAP_ENABLED=false` (padrão), a autenticação é só JDBC/local.

---

## 3. Active Directory (LDAP) — opcional

Referência: `config/ldap/ldap-settings.yaml` e variáveis `.env` / ConfigMap / Secret.

| Campo | Variável | Descrição |
|-------|----------|-----------|
| Liga LDAP | `LDAP_ENABLED` | `true` / `false` (padrão `false`) |
| Servidor | `LDAP_HOSTNAME` | Ex.: `ldap.aqne.jus.br` |
| Porta | `LDAP_PORT` | `636` (LDAPS) ou `389` |
| Domínio | yaml `ldap.domain` | `aqne.jus.br` |
| Base usuários / grupos | `LDAP_USER_BASE_DN` / `LDAP_GROUP_BASE_DN` | DNs do AD |
| Atributo UID | `LDAP_USERNAME_ATTRIBUTE` | `sAMAccountName` |
| Bind | `LDAP_SEARCH_BIND_DN` / `LDAP_SEARCH_BIND_PASSWORD` | Conta de serviço |
| CA | `LDAP_CA_CHAIN_FILE` | PEM em `/etc/guacamole/certs/` |

Procedimento: preencher CA e secrets → `LDAP_ENABLED=true` → reiniciar Guacamole → testar login AD **mantendo** `guacadmin` local.

| Grupo AD | Papel |
|----------|-------|
| `GG-SegPortal-Admin` | Administrador |
| `GG-SegPortal-Usuarios` | Usuário |
| `GG-SegPortal-Financeiro` / `Consulta` / `Externo` | Negócio |

Ver [ROLES.md](ROLES.md).

---

## 4. MFA via RADIUS

```bash
MFA_ENABLED=true
MFA_RADIUS_HOSTNAME=radius.aqne.jus.br
MFA_RADIUS_PORT=1812
MFA_RADIUS_SECRET=<shared_secret>
```

Recomendado com LDAP. Com `MFA_ENABLED=false`, o entrypoint remove chaves `radius-*`.

---

## 5. Guacamole e PostgreSQL

| Variável | Descrição | Padrão |
|----------|-----------|--------|
| `POSTGRES_DB` | Banco | `guacamole_db` |
| `POSTGRES_USER` | Usuário | `guacamole_user` |
| `POSTGRES_PASSWORD` | Senha | *(obrigatório)* |
| `SESSION_TIMEOUT_MINUTES` | Timeout | `60` |

O serviço **`segportal-bootstrap`** aplica schema (se necessário), papéis e o navegador padrão — não dependa de seed manual.

```bash
./scripts/bootstrap-segportal.sh   # idempotente
```

---

## 6. Navegador HTML padrão (automático)

| Item | Valor |
|------|-------|
| Serviço | `web-browser` (Firefox / VNC `:5900`) |
| Conexão Guacamole | **Navegador Web SegPortal** |
| Permissão | `READ` para todos os usuários no boot |
| Docs | [CONNECTIONS.md](CONNECTIONS.md) |

Compose e Job K8s (`k8s/bootstrap`) já incluem o bootstrap. Imagem: `services/web-browser/Dockerfile` (`SECURE_CONNECTION=0`, sem senha VNC na rede interna).

![Fluxo do navegador padrão](images/usage-browser.jpg)

---

## 7. Proxy de egress (Squid)

Arquivos: `config/proxy/squid.conf` e `services/egress-proxy/`. Serviço Compose/K8s: `proxy-egress`.

Revise a whitelist antes de produção.

---

## 8. Branding AQNE

Arquivos em `services/guacamole/branding/`.

---

## 9. Kubernetes / Rancher

```bash
kubectl create namespace segportal
# secrets a partir de k8s/*/secret.example.yaml
kubectl apply -k k8s/overlays/production
# Job segportal-bootstrap cria navegador padrão
kubectl -n segportal wait --for=condition=complete job/segportal-bootstrap --timeout=300s
```

---

## 10. Pedidos de conexão

Usuário solicita; admin aprova. Política: `config/connections/requests.yaml`.

```bash
./scripts/request-connection.sh usuario "RDP X" rdp 10.10.20.51 3389 "Justificativa"
./scripts/approve-connection-request.sh 1
```

Cadastro manual na UI (Settings → Connections) continua válido para o admin.

---

## 11. Validação pós-configuração

- [ ] Login `guacadmin` funciona **sem** LDAP
- [ ] Conexão **Navegador Web SegPortal** aparece para admin e usuário
- [ ] Senha do admin alterada em produção
- [ ] (Se LDAP) login AD + CA válida
- [ ] Usuário normal não vê Settings administrativos
- [ ] Admin consegue aprovar pedidos

```bash
pytest tests -v
./scripts/validate-k8s.sh
```

## Referências

- [LOCAL_ADMIN.md](LOCAL_ADMIN.md)
- [ROLES.md](ROLES.md)
- [CONNECTIONS.md](CONNECTIONS.md)
- [SECURITY.md](SECURITY.md)
- [MANUAL.md](MANUAL.md)
