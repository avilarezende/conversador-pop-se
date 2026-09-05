## Descrição

<!-- Descreva a mudança e o motivo (issue, demanda AQNE, etc.) -->

## Tipo de alteração

- [ ] Correção de bug
- [ ] Nova funcionalidade
- [ ] Alteração de configuração / infraestrutura
- [ ] Documentação
- [ ] Refatoração

## Checklist

- [ ] `pytest` passa localmente
- [ ] `./scripts/validate-k8s.sh` passa (se alterou `k8s/`)
- [ ] Segredos **não** commitados (use `.env` / Secrets K8s)
- [ ] Documentação atualizada (`docs/`, `README.md`)
- [ ] Imagens Docker constroem com `context: .` na raiz

## Ambiente afetado

- [ ] Desenvolvimento (Docker Compose)
- [ ] Staging
- [ ] Produção (Rancher / Fleet)

## Segurança

- [ ] Revisão de impacto em LDAP/MFA
- [ ] Whitelist do proxy egress revisada (se aplicável)

## Screenshots / evidências

<!-- Mockup, logs, capturas de tela do portal -->
