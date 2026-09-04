# Mockup do portal

O mockup visual do SegPortal está disponível como imagem JPG e preview HTML:

- **[segportal-mockup.jpg](../images/segportal-mockup.jpg)** — imagem estática para o GitHub
- **[segportal-preview.html](segportal-preview.html)** — preview interativo com papéis

### Preview interativo (papéis)

```bash
cd docs/mockup
python3 -m http.server 8765
# http://localhost:8765/segportal-preview.html
```

| Papel | Login | Senha | MFA |
|-------|-------|-------|-----|
| Administrador | `guacadmin` | `guacadmin` | `123456` |
| Usuário | `usuario` | `usuario` | `123456` |

O admin vê o painel de sessões e configuração; o usuário vê apenas o recurso do seu contexto.

Para o manual completo: [ROLES.md](../ROLES.md) e [MANUAL.md](../MANUAL.md).
