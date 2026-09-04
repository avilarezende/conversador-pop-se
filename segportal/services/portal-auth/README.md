# Portal Auth / Admin settings

Módulo de apoio para autenticação e **configuração administrativa** do SegPortal.

## Responsabilidades

1. Validação MFA (RADIUS) quando habilitada
2. Referência dos apontamentos LDAP editáveis pelo administrador
3. Manutenção do modelo “LDAP opcional + usuários locais sempre ativos”

## LDAP configurável

Fonte da verdade humana: `config/ldap/ldap-settings.yaml`

Campos principais: servidor, porta, criptografia, domínio, base DN, atributo UID,
bind DN, certificado do servidor e cadeia de CAs.

Comportamento no container (`services/guacamole/entrypoint.sh`):

- `LDAP_ENABLED=false` → remove `ldap-*` do `guacamole.properties` (só JDBC)
- `LDAP_ENABLED=true` → aplica apontamentos e importa CA no truststore Java

## Admin padrão

Sempre existe a conta local `guacadmin` (senha inicial `guacadmin`), independente do LDAP.

- Trocar senha: `scripts/change-local-password.sh`
- Desativar/excluir: `scripts/delete-local-user.sh`

Documentação: `docs/LOCAL_ADMIN.md`.

## Extensão futura

API/UI administrativa (FastAPI) para gravar `ldap-settings` em ConfigMap/Secret
sem redeploy manual — encaixar neste diretório quando o time avançar a esteira.
