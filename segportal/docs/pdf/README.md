# Manuais em PDF

| Arquivo | Público |
|---------|---------|
| [manual-usuario-final.pdf](manual-usuario-final.pdf) | Usuário final (servidores, magistrados, colaboradores) |

Fonte HTML: [`../manual-usuario-final.html`](../manual-usuario-final.html).

Para regenerar:

```bash
cd docs
google-chrome --headless=new --disable-gpu --no-sandbox \
  --allow-file-access-from-files \
  --print-to-pdf=pdf/manual-usuario-final.pdf \
  --print-to-pdf-no-header \
  file://$PWD/manual-usuario-final.html
```
