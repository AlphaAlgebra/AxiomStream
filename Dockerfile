# Use a lightweight, standardized Python runtime core
FROM python:3.11-slim

# Establish explicit working directory boundaries
WORKDIR /app

# Copy dependency manifest definitions into the build workspace
COPY requirements.txt .

# Clear local pipeline package memory caches to bypass storage overhead limits
RUN pip install --no-cache-dir -r requirements.txt

# Copy the complete source execution layout into the image path
COPY src/ ./src/

# Instruct Python to correctly map system paths for module discovery
ENV PYTHONPATH="${PYTHONPATH}:/app"

# Configure the container to trigger the master pipeline script automatically on launch
CMD ["python3", "-m", "src.infrastructure.master_pipeline"]
