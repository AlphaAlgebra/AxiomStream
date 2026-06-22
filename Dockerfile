# ==========================================
# STAGE 1: Dependency Builder Core
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install system compilation packages if underlying dependencies need extensions
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy python packaging requirements manifest 
COPY requirements.txt .

# Install dependencies to a localized target wheels directory to keep runtime lean
RUN pip install --no-cache-dir --user -r requirements.txt


# ==========================================
# STAGE 2: Secure Runtime Image
# ==========================================
FROM python:3.11-slim AS runtime

WORKDIR /app

# Create a non-privileged system application user for Zero-Trust security postures
RUN groupadd -g 10001 appuser && \
    useradd -u 10001 -g appuser -m -s /sbin/nologin appuser

# Extract pre-compiled python dependencies directly from the builder node environment
COPY --from=builder /root/.local /home/appuser/.local
COPY . .

# Set environment runtime properties to sync compiled locations and drops root privileges
ENV PATH=/home/appuser/.local/bin:$PATH
ENV PYTHONPATH=/app
RUN chown -R appuser:appuser /app

USER appuser

# Default execution entrypoint runs your newly designed live streaming pipeline bridge
CMD ["python", "-m", "src.infrastructure.streaming_bridge"]
