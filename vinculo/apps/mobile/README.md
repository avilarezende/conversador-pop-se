# Vínculo Mobile (esqueleto)

Cliente móvel alvo: **Flutter** (iOS/Android), alinhado ao monólito modular via API HTTP + plugins nativos.

## Módulos de UI previstos

| Área | Telas | Depende de |
|------|-------|------------|
| Onboarding | identidade, geração de chaves PQC | `identity`, `crypto_pqc` |
| Grafo | contatos 1º grau, reconhecimento de entidade, QR de evento | `trust_graph` |
| Chat | texto, anexos | `ledger`, `media` |
| Mídia | picker da galeria, exportação com WM | `media` |
| Chamada | voz/vídeo (flag) | `realtime` |

## Estrutura sugerida (a criar na fase 1)

```
apps/mobile/
  pubspec.yaml
  lib/
    main.dart
    src/
      app.dart
      features/
        identity/
        trust_graph/
        chat/
        media/
        realtime/
      core/
        api_client.dart
        theme.dart
```

Este diretório contém apenas o **placeholder** e o contrato de features — sem app Flutter compilável ainda (fase 0 = planejamento + backend skeleton).
