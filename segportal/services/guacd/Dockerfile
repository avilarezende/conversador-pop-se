# SegPortal AQNE — guacd (Guacamole proxy daemon)
ARG GUACD_VERSION=1.5.5

FROM guacamole/guacd:${GUACD_VERSION}

LABEL org.opencontainers.image.title="segportal-guacd" \
      org.opencontainers.image.description="Guacamole proxy daemon for SegPortal AQNE" \
      org.opencontainers.image.vendor="AQNE"

USER root
RUN apk add --no-cache netcat-openbsd
USER guacd

EXPOSE 4822

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD nc -z localhost 4822 || exit 1
