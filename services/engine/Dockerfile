FROM python:3.12-slim@sha256:02108f5d322dd89f1c9e552442c25acb0543dfdbc455693a5599624f20d9155d

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY services/engine/requirements.lock /app/requirements.lock
RUN --mount=type=secret,id=egress_ca \
    if [ -f /run/secrets/egress_ca ]; then export PIP_CERT=/run/secrets/egress_ca; fi; \
    pip install --no-cache-dir --require-hashes -r requirements.lock

COPY shared /app/shared
COPY services/engine/app /app/app

ENV PYTHONPATH=/app
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
