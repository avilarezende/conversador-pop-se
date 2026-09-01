# portal-auth (futuro)

Módulo reservado para integrações de autenticação complementares ao Guacamole LDAP/MFA do SegPortal TJSE.

## Escopo planejado

- Validação de claims OIDC/SAML para federação com IdP corporativo
- Webhook de auditoria pós-login (SIEM)
- Políticas de sessão por perfil AD

## Estado atual

A autenticação é realizada nativamente pelo **Guacamole** com a extensão `guacamole-auth-ldap` 1.5.5 e **RADIUS** para MFA. Este diretório documenta a evolução futura; não há serviço implantado nesta versão.

## Referências

- [CONFIGURATION.md](../../docs/CONFIGURATION.md) — LDAP e MFA
- [SECURITY.md](../../docs/SECURITY.md) — controles de autenticação
