# SegPortal AQNE — Guacamole web application
# Build context: repository root (docker-compose / CI)
ARG GUACAMOLE_VERSION=1.5.5

FROM guacamole/guacamole:${GUACAMOLE_VERSION}

USER root

# Re-declare build args for use in RUN (ARG before FROM is not available here)
ARG GUACAMOLE_VERSION=1.5.5
ARG LDAP_EXTENSION_VERSION=1.5.5
ARG GUACAMOLE_BINARY_BASE=https://dlcdn.apache.org/guacamole
RUN apt-get update && apt-get install -y --no-install-recommends curl gettext-base \
    && mkdir -p /etc/guacamole/extensions /etc/guacamole/certs /tmp/guac-ext \
    && curl -fsSL \
      "${GUACAMOLE_BINARY_BASE}/${GUACAMOLE_VERSION}/binary/guacamole-auth-ldap-${LDAP_EXTENSION_VERSION}.tar.gz" \
      -o /tmp/guac-ext/ldap.tar.gz \
    && tar -xzf /tmp/guac-ext/ldap.tar.gz -C /tmp/guac-ext \
    && cp "/tmp/guac-ext/guacamole-auth-ldap-${LDAP_EXTENSION_VERSION}/guacamole-auth-ldap-${LDAP_EXTENSION_VERSION}.jar" \
      "/etc/guacamole/extensions/guacamole-auth-ldap-${LDAP_EXTENSION_VERSION}.jar" \
    && rm -rf /tmp/guac-ext \
    && apt-get purge -y curl && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

# AQNE branding and configuration
COPY config/guacamole/guacamole.properties /etc/guacamole/guacamole.properties.template
COPY config/ldap/ldap-settings.yaml /etc/guacamole/ldap-settings.yaml
COPY services/guacamole/branding/ /etc/guacamole/branding/
COPY services/guacamole/entrypoint.sh /opt/segportal/entrypoint.sh

RUN chmod +x /opt/segportal/entrypoint.sh \
    && chown -R guacamole:guacamole /etc/guacamole /opt/segportal

USER guacamole

ENV GUACAMOLE_HOME=/etc/guacamole
EXPOSE 8080

ENTRYPOINT ["/opt/segportal/entrypoint.sh"]
CMD ["/opt/guacamole/bin/start.sh", "--foreground"]
