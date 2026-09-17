# SegPortal — navegador HTML5 clientless (Firefox via VNC)
# Imagem própria (Xvfb + x11vnc + Firefox ESR) — compatível com guacd/Guacamole.
# Acessado apenas via guacd na rede interna (porta 5900).
FROM debian:bookworm-slim

LABEL org.opencontainers.image.title="segportal-web-browser"
LABEL org.opencontainers.image.description="Navegador HTML padrão SegPortal AQNE (VNC→Guacamole)"

ENV DEBIAN_FRONTEND=noninteractive \
    DISPLAY=:99 \
    DISPLAY_WIDTH=1280 \
    DISPLAY_HEIGHT=800 \
    VNC_PASSWORD=segport1 \
    VNC_PORT=5900 \
    FF_OPEN_URL=https://example.com \
    LANG=C.UTF-8 \
    MOZ_DISABLE_CONTENT_SANDBOX=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        dbus \
        dbus-x11 \
        firefox-esr \
        fonts-liberation \
        fonts-noto-color-emoji \
        netcat-openbsd \
        openbox \
        procps \
        x11vnc \
        xvfb \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /opt/segportal /home/browser \
    && useradd --create-home --home-dir /home/browser --shell /bin/bash browser \
    && chown -R browser:browser /home/browser /opt/segportal

COPY start-browser.sh /opt/segportal/start-browser.sh
RUN chmod 755 /opt/segportal/start-browser.sh

EXPOSE 5900

HEALTHCHECK --interval=15s --timeout=5s --start-period=25s --retries=10 \
  CMD nc -z 127.0.0.1 5900 || exit 1

USER browser
WORKDIR /home/browser

CMD ["/opt/segportal/start-browser.sh"]
