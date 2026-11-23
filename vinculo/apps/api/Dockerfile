FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml README.md ./
COPY packages ./packages
COPY apps/api ./apps/api
COPY config ./config

RUN pip install --no-cache-dir -e .

ENV PYTHONPATH=/app/packages:/app/apps/api
ENV MODULES_CONFIG_PATH=/app/config/modules.yaml

EXPOSE 8090
CMD ["uvicorn", "vinculo_api.main:app", "--host", "0.0.0.0", "--port", "8090"]
