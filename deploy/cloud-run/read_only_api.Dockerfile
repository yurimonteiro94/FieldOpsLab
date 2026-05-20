FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

COPY services ./services
COPY analysis/reports ./analysis/reports
COPY platform/contracts ./platform/contracts

RUN useradd --create-home --shell /usr/sbin/nologin fieldops \
    && chown -R fieldops:fieldops /app

USER fieldops

EXPOSE 8080

CMD ["sh", "-c", "python services/api/fieldops_http_server.py --host 0.0.0.0 --port ${PORT}"]