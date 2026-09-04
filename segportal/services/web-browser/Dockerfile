# SegPortal — navegador HTML5 clientless (Firefox via VNC)
# Acessado pelo Guacamole; disponível por padrão a todos os usuários.
FROM jlesage/firefox:v24.11.1

LABEL org.opencontainers.image.title="segportal-web-browser"
LABEL org.opencontainers.image.description="Navegador HTML padrão SegPortal TJSE (VNC→Guacamole)"

# Porta VNC usada pelo guacd (GUI web do jlesage fica em 5800)
EXPOSE 5900 5800

ENV DISPLAY_WIDTH=1280 \
    DISPLAY_HEIGHT=800 \
    DARK_MODE=0 \
    FF_OPEN_URL=https://www.tjse.jus.br
