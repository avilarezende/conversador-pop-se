# Segurança — SegPortal AQNE

Controles de segurança do portal ZTNA baseado em Guacamole.

## Princípios Zero Trust

1. **Verificar explicitamente** — autenticação local e/ou LDAP + MFA antes de qualquer recurso
2. **Menor privilégio** — conexões mapeadas por grupo; pedidos extras exigem aprovação
3. **Assumir violação** — sessões isoladas, timeout agressivo
4. **Micro-segmentação** — pods e redes separados por função

## Autenticação

| Camada | Controle |
|--------|----------|
| Local (JDBC) | Sempre ativo — admin padrão `guacadmin` independente do LDAP |
| Identidade AD | Opcional (`LDAP_ENABLED=true`) via LDAPS |
| MFA | RADIUS corporativo — opcional |
| Sessão | Timeout 60 min inatividade, limite de conexões simultâneas |

Conta de serviço `svc-segportal` só é necessária quando LDAP está habilitado.  
Guia do admin local: [LOCAL_ADMIN.md](LOCAL_ADMIN.md).

## Papéis e isolamento

| Papel | Grupo | Visão de sessões | Configuração |
|-------|-------|------------------|--------------|
| **Administrador** | `segportal-admins` / `GG-SegPortal-Admin` | Todas (`ADMINISTER`) | Completa + aprovações |
| **Usuário** | `segportal-users` / `GG-SegPortal-Usuarios` | Apenas a própria | Nenhuma |

Usuários normais recebem `READ` no **Navegador Web SegPortal** (padrão) e nas conexões dos grupos de negócio / aprovadas. Detalhes: [ROLES.md](ROLES.md) · [CONNECTIONS.md](CONNECTIONS.md).

## Navegador HTML padrão

| Controle | Medida |
|----------|--------|
| Exposição VNC | Apenas rede interna (guacd → `web-browser:5900`) |
| Senha VNC | Desabilitada na rede do cluster/compose |
| TLS VNC | `SECURE_CONNECTION=0` (Guacamole não usa VNC TLS) |
| Egress | Sites externos passam pelo Squid (`proxy-egress`) |
| Criação de conexões | Usuário **não** cria sozinho — aprovação admin |

## Comunicação

- **TLS** em todo tráfego externo (Ingress + cert-manager)
- **LDAPS** para bind e busca de usuários (quando LDAP ligado)
- Tráfego interno do cluster: rede CNI isolada (NetworkPolicies recomendadas)

## Egress controlado

O proxy Squid permite apenas destinos na whitelist (ex.: `*.aqne.jus.br`, `*.jus.br`, `*.gov.br`). Demais destinos são **negados**. O IP de saída é o institucional do tribunal.

## Dados sensíveis

- Secrets Kubernetes para credenciais (não em ConfigMaps)
- `.env` e `secrets/` no `.gitignore`
- Senha inicial `guacadmin` **deve** ser alterada em produção

## Hardening de containers

- Imagens base oficiais Guacamole 1.5.5 / jlesage Firefox
- Usuário não-root onde aplicável
- Health checks e limites de recursos (requests/limits)
- Sem privilégios elevados nos pods

## Auditoria

- Pedidos de conexão registrados em `segportal_connection_request`
- Encaminhar logs Squid e Guacamole ao SIEM
- Retenção conforme política AQNE

## Resposta a incidentes

1. Revogar sessões: reiniciar deployment `guacamole`
2. Rotacionar senhas/secrets LDAP e RADIUS
3. Bloquear egress: escalar `proxy-egress` para 0 ou NetworkPolicy deny-all
4. Isolar `web-browser` se houver abuso de navegação

## Conformidade

- Acesso remoto substitui VPN legada com controles equivalentes ou superiores
- Dados processuais acessados via RDP/VNC permanecem nos sistemas de origem
- Revisão periódica de grupos AD, aprovações pendentes e whitelist Squid

## Referências

- [CONFIGURATION.md](CONFIGURATION.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
- [CONNECTIONS.md](CONNECTIONS.md)
- [MANUAL.md](MANUAL.md)
