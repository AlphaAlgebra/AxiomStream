# Stage 1: Build dependencies and wheels
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ python3-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final minimal production runtime environment
FROM python:3.11-slim AS runtime
WORKDIR /app

# Create a secure non-privileged system user
RUN groupadd -r architect && useradd -r -g architect formaluser
USER formaluser

# Copy installed packages from builder stage
COPY --from=builder /root/.local /home/formaluser/.local
COPY src/ ./src/

ENV PATH=/home/formaluser/.local/bin:$PATH
ENV PYTHONPATH=.

# Execute the asynchronous multi-agent orchestrator processing pool
CMD ["python", "src/infrastructure/orchestrator.py"]
