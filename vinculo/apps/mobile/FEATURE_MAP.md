# Mapa de features → pacotes

| Feature Flutter | Pacote Python / port | Notas |
|-----------------|----------------------|-------|
| Registrar identidade | `vinculo_identity` + `PqcCryptoPort` | Chaves geradas no device |
| Aceitar contato / QR | `TrustGraphPort.add_edge` | Âncora de evento opcional |
| Abrir chat | `TrustGraphPort.can_open_channel` | Fail-closed |
| Enviar mensagem | `ConversationLedgerPort.append` | Ciphertext no device |
| Importar da galeria | `MediaExportPort.store` | Cópia para cofre |
| Exportar mídia | `MediaExportPort.export_with_watermark` | Obrigatório |
| Chamada A/V | `RealtimeSessionPort` | `realtime_av.enabled` |
