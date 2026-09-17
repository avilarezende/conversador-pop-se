FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEMO_SHARES_ROOT=/data/shares \
    PORTAL_PORT=8090

COPY services/portal-auth/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY config /app/config
COPY services/portal-auth /app/services/portal-auth

WORKDIR /app/services/portal-auth
EXPOSE 8090

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8090"]
