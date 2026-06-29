FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ python3-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

FROM python:3.11-slim AS runtime
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends redis-server && rm -rf /var/lib/apt/lists/*

RUN groupadd -r architect && useradd -r -g architect formaluser
RUN mkdir -p /var/run/redis /var/log/redis /var/lib/redis && \
    chown -R formaluser:architect /var/run/redis /var/log/redis /var/lib/redis
USER formaluser

COPY --from=builder /root/.local /home/formaluser/.local
ENV PATH=/home/formaluser/.local/bin:$PATH
ENV PYTHONPATH=.

COPY src/ ./src/
COPY tests/ ./tests/
COPY locustfile.py .
COPY requirements.txt .

# --- EXPOSE THE NATIVE PROMETHEUS SCRAPE ENDPOINT PORT ---
EXPOSE 8000
EXPOSE 6379

RUN cat << 'INNER_EOF' > entrypoint.sh
#!/bin/sh
echo "🗄️ Starting localized in-memory Redis server background instance..."
redis-server --daemonize yes --port 6379 --protected-mode no --dir /var/lib/redis

echo "⚡ Booting high-throughput low-latency symbolic orchestration loop engine..."
exec python src/infrastructure/orchestrator.py
INNER_EOF

RUN chmod +x entrypoint.sh
CMD ["./entrypoint.sh"]
