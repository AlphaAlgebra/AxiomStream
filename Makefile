.PHONY: install test build run clean

# Setup local environment and isolated packages
install:
	python3 -m venv venv && \
	. venv/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt

# Run property-based validation checks with zero disk-cache dependencies
test:
	python3 -m pytest -vv -p no:cacheprovider tests/test_symbolic_engine.py

# Build the enterprise-grade secure container image
build:
	docker build -t axiomstream-engine:latest .

# Run local execution pipeline loops
run:
	python3 -m src.infrastructure.orchestrator

# Force-clear compilation byte-code and cache artifacts
clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	rm -rf .pytest_cache
