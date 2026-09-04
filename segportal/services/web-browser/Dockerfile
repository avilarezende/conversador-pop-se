# SegPortal — navegador HTML5 clientless (Firefox via VNC)
# Habilitado por padrão no boot (bootstrap + conexão Guacamole).
# Acessado apenas via guacd na rede interna (porta 5900).
FROM jlesage/firefox:v24.11.1

LABEL org.opencontainers.image.title="segportal-web-browser"
LABEL org.opencontainers.image.description="Navegador HTML padrão SegPortal TJSE (VNC→Guacamole)"

EXPOSE 5900 5800

# Sem senha VNC e sem TLS: Guacamole fala VNC plain na rede do compose/K8s.
# KEEP_APP_RUNNING reinicia o Firefox se fechar.
ENV DISPLAY_WIDTH=1280 \
    DISPLAY_HEIGHT=800 \
    DARK_MODE=0 \
    KEEP_APP_RUNNING=1 \
    SECURE_CONNECTION=0 \
    VNC_LISTENING_PORT=5900 \
    WEB_LISTENING_PORT=5800 \
    FF_OPEN_URL=https://www.tjse.jus.br
