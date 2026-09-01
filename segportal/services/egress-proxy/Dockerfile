# SegPortal TJSE — institutional egress proxy (Squid)
FROM ubuntu/squid:6.6-24.04_edge

LABEL org.opencontainers.image.title="segportal-egress-proxy" \
      org.opencontainers.image.description="Controlled HTTP egress for SegPortal TJSE" \
      org.opencontainers.image.vendor="TJSE"

USER root
COPY services/egress-proxy/squid.conf /etc/squid/squid.conf
RUN mkdir -p /var/spool/squid /var/log/squid \
    && chown -R proxy:proxy /var/spool/squid /var/log/squid \
    && squid -z -f /etc/squid/squid.conf || true

EXPOSE 3128

HEALTHCHECK --interval=10s --timeout=5s --retries=3 \
  CMD nc -z localhost 3128 || exit 1

USER proxy
CMD ["squid", "-N", "-f", "/etc/squid/squid.conf"]
