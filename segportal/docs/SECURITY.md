# Segurança — SegPortal TJSE

Controles de segurança do portal ZTNA baseado em Guacamole.

## Princípios Zero Trust

1. **Verificar explicitamente** — LDAP + MFA antes de qualquer recurso
2. **Menor privilégio** — conexões mapeadas por grupo AD
3. **Assumir violação** — sessões isoladas, timeout agressivo
4. **Micro-segmentação** — pods e redes separados por função

## Autenticação

| Camada | Controle |
|--------|----------|
| Identidade | Active Directory `tjse.jus.br` via LDAPS (porta 636) |
| MFA | RADIUS corporativo (PAP) — obrigatório em produção |
| Sessão | Timeout 60 min inatividade, máx. 3 conexões simultâneas |

Conta de serviço `svc-segportal` com permissões mínimas de leitura no AD.

## Papéis e isolamento

| Papel | Grupo | Visão de sessões | Configuração |
|-------|-------|------------------|--------------|
| **Administrador** | `segportal-admins` / `GG-SegPortal-Admin` | Todas (`ADMINISTER`) | Completa |
| **Usuário** | `segportal-users` / `GG-SegPortal-Usuarios` | Apenas a própria | Nenhuma |

Usuários normais recebem somente `READ` nas conexões dos grupos de negócio. Detalhes: [ROLES.md](ROLES.md).

## Comunicação

- **TLS** em todo tráfego externo (Ingress + cert-manager)
- **LDAPS** para bind e busca de usuários
- Tráfego interno cluster: rede CNI isolada (NetworkPolicies recomendadas)

## Egress controlado

O proxy Squid permite apenas destinos na whitelist:

- `*.tjse.jus.br`
- `*.jus.br`, `*.gov.br`
- `*.pje.jus.br`, `*.cnj.jus.br`

Demais destinos são **negados**. O IP de saída é o institucional do tribunal.

## Dados sensíveis

- Senhas nunca persistidas pelo Guacamole (auth delegada ao AD)
- Secrets Kubernetes para credenciais (não em ConfigMaps)
- `.env` e `secrets/` no `.gitignore`

## Hardening de containers

- Imagens base oficiais Guacamole 1.5.5
- Usuário não-root (`guacamole`, `proxy`)
- Health checks e limites de recursos (requests/limits)
- Sem privilégios elevados nos pods

## Auditoria

Recomendações para produção:

- Encaminhar logs de acesso Squid ao SIEM
- Habilitar auditoria de login Guacamole (plugin futuro em `plugins/`)
- Retenção de logs conforme política TJSE

## Resposta a incidentes

1. Revogar sessões: reiniciar deployment `guacamole`
2. Rotacionar `LDAP_SEARCH_BIND_PASSWORD` e `MFA_RADIUS_SECRET`
3. Bloquear egress: escalar `proxy-egress` para 0 ou aplicar NetworkPolicy deny-all

## Conformidade

- Acesso remoto substitui VPN legada com controles equivalentes ou superiores
- Dados processuais acessados via RDP/VNC permanecem nos sistemas de origem
- Revisão periódica de grupos AD e whitelist Squid

## Referências

- [CONFIGURATION.md](CONFIGURATION.md)
- [ARCHITECTURE.md](ARCHITECTURE.md)
