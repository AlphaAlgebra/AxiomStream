# Stage 1: Build dependencies and wheels securely
FROM python:3.11-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends gcc g++ python3-dev && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Stage 2: Final ultra-low latency runtime image
FROM python:3.11-slim AS runtime
WORKDIR /app

# Setup non-privileged application user context
RUN groupadd -r architect && useradd -r -g architect formaluser
USER formaluser

# Copy python packages and path specifications
COPY --from=builder /root/.local /home/formaluser/.local
ENV PATH=/home/formaluser/.local/bin:$PATH
ENV PYTHONPATH=.

# Copy complete repository layer configurations required for test collections
COPY src/ ./src/
COPY tests/ ./tests/
COPY locustfile.py .
COPY requirements.txt .

# Start the low-latency streaming loop daemon
CMD ["python", "src/infrastructure/orchestrator.py"]
