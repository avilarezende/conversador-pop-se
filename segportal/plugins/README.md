# Plugins Guacamole — SegPortal TJSE

Diretório reservado para extensões customizadas do Apache Guacamole além do `guacamole-auth-ldap` incluído na imagem base.

## Como adicionar um plugin

1. Compile ou obtenha o JAR da extensão compatível com Guacamole **1.5.5**
2. Coloque o artefato em `plugins/<nome>/`
3. Atualize `services/guacamole/Dockerfile` para copiar o JAR para `/etc/guacamole/extensions/`
4. Documente variáveis em [CONFIGURATION.md](../docs/CONFIGURATION.md)
5. Adicione testes em `tests/test_config.py` se houver novas propriedades

## Exemplos de extensões candidatas

| Plugin | Uso |
|--------|-----|
| `guacamole-auth-totp` | MFA TOTP nativo (alternativa ao RADIUS) |
| `guacamole-auth-duo` | Integração Duo Security |
| Custom audit | Log estruturado para SIEM TJSE |

## Convenções

- Versão do plugin deve coincidir com a versão do Guacamole (1.5.5)
- Não commitar segredos; use Secrets do Kubernetes ou variáveis de ambiente
- Plugins devem ser auditáveis e aprovados pela área de segurança TJSE
