FROM python:3.12-slim@sha256:02108f5d322dd89f1c9e552442c25acb0543dfdbc455693a5599624f20d9155d
WORKDIR /app
COPY services/modules/sources/requirements.lock /app/requirements.lock
RUN --mount=type=secret,id=egress_ca \
    if [ -f /run/secrets/egress_ca ]; then export PIP_CERT=/run/secrets/egress_ca; fi; \
    pip install --no-cache-dir --require-hashes -r /app/requirements.lock
COPY shared /app/shared
COPY services/modules/sources/collectors /app/collectors
COPY services/modules/sources/main.py /app/main.py
COPY config /app/config
ENV PYTHONPATH=/app
ENV CONFIG_PATH=/app/config
CMD ["python", "main.py"]
