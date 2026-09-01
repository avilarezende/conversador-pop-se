# SegPortal TJSE — Guacamole web application
# Build context: repository root (docker-compose / CI)
ARG GUACAMOLE_VERSION=1.5.5

FROM guacamole/guacamole:${GUACAMOLE_VERSION}

USER root

# LDAP authentication extension (Apache Guacamole 1.5.5)
# Artifact: guacamole-auth-ldap-1.5.5.jar
ARG LDAP_EXTENSION_VERSION=1.5.5
RUN mkdir -p /etc/guacamole/extensions /etc/guacamole/lib \
    && curl -fsSL \
      "https://archive.apache.org/dist/guacamole/${GUACAMOLE_VERSION}/binary/guacamole-auth-ldap-${LDAP_EXTENSION_VERSION}.jar" \
      -o "/etc/guacamole/extensions/guacamole-auth-ldap-${LDAP_EXTENSION_VERSION}.jar"

# TJSE branding and configuration
COPY config/guacamole/guacamole.properties /etc/guacamole/guacamole.properties.template
COPY services/guacamole/branding/ /etc/guacamole/branding/
COPY services/guacamole/entrypoint.sh /opt/segportal/entrypoint.sh

RUN chmod +x /opt/segportal/entrypoint.sh \
    && chown -R guacamole:guacamole /etc/guacamole

USER guacamole

ENV GUACAMOLE_HOME=/etc/guacamole
EXPOSE 8080

ENTRYPOINT ["/opt/segportal/entrypoint.sh"]
CMD ["/opt/guacamole/bin/start.sh", "--foreground"]
