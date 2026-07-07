import asyncio
import threading
from prometheus_client import start_http_server, Counter, Gauge, Histogram

# 1. Audit-Grade Counters and Gauges
TRANSACTION_AUDIT_TOTAL = Counter(
    'axiomstream_audit_transactions_total',
    'Total validated transactions for legal state auditing',
    ['state_machine_id', 'status', 'invariant_signature']
)

PIPELINE_LATENCY_MESH = Histogram(
    'axiomstream_mesh_latency_seconds',
    'Absolute end-to-end execution latency per validation cell',
    ['cell_id'],
    buckets=(0.0005, 0.001, 0.005, 0.01, 0.05, 0.1, 0.5)
)

KAFKA_PARTITION_LAG = Gauge(
    'axiomstream_mesh_kafka_lag',
    'Unprocessed event offset delta per individual stream partition',
    ['topic', 'partition_id']
)

def launch_isolated_telemetry_mesh(port: int = 8000):
    """
    Spins up the scraping infrastructure endpoint on an independent, 
    non-blocking network socket for the metrics harvest.
    """
    # Start server in an independent background runner to protect core asyncio runtime loops
    server_thread = threading.Thread(target=start_http_server, args=(port,), daemon=True)
    server_thread.start()
    print(f"[METRICS MESH] Node listening on server socket endpoint: http://localhost:{port}/metrics")
