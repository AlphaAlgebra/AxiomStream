import asyncio
import os
import sys
import random
import json
from concurrent.futures import ProcessPoolExecutor
from src.engine.symbolic_solver import SymbolicStateVerifier
from prometheus_client import start_http_server, Counter, Histogram

TRANSACTION_COUNT = Counter('axiom_transactions_total', 'Total processed transaction stream payloads', ['status'])
CACHE_LOOKUP_COUNT = Counter('axiom_cache_lookups_total', 'Total Redis memory cache lookups', ['result'])
LATENCY_HISTOGRAM = Histogram('axiom_transaction_latency_seconds', 'Sustained validation loop latency metrics')

_PROCESS_POOL: ProcessPoolExecutor = None
_REDIS_CLIENT = None

def get_compute_pool() -> ProcessPoolExecutor:
    """Initializes or returns a cached multi-core execution process pool layout."""
    global _PROCESS_POOL
    if _PROCESS_POOL is None:
        max_workers = os.cpu_count() or 2
        _PROCESS_POOL = ProcessPoolExecutor(max_workers=max_workers)
    return _PROCESS_POOL

async def get_redis_client():
    """Initializes an asynchronous connection pool context to a local or cloud Redis instance."""
    global _REDIS_CLIENT
    if _REDIS_CLIENT is None:
        try:
            import redis.asyncio as aioredis
            redis_host = os.getenv("REDIS_HOST", "localhost")
            _REDIS_CLIENT = aioredis.Redis(host=redis_host, port=6379, decode_responses=True)
            await asyncio.wait_for(_REDIS_CLIENT.ping(), timeout=1.0)
            print("🚀 [CACHE-INFRA] Asynchronous Redis connection pool established successfully.")
        except Exception:
            print("⚠️ [CACHE-INFRA] Redis host unreachable. Operating engine under fallback parameters.")
            _REDIS_CLIENT = False
    return _REDIS_CLIENT

def _cpu_bound_symbolic_task(expression: str) -> dict:
    """Isolated heavy algebraic processing callback running in a clean OS worker process."""
    verifier = SymbolicStateVerifier()
    return verifier.verify_transaction_safety(expression)

async def process_stream_transaction(stream_event: str):
    """Asynchronous transaction processor equipped with sub-millisecond Redis caching and Prometheus metrics."""
    loop = asyncio.get_running_loop()
    pool = get_compute_pool()
    redis = await get_redis_client()
    cache_key = f"axiom_verify:{stream_event}"
    
    with LATENCY_HISTOGRAM.time():
        if redis:
            try:
                cached_result = await redis.get(cache_key)
                if cached_result:
                    result = json.loads(cached_result)
                    print(f"⚡ [REDIS-CACHE-HIT] Instant lookup successful for payload: '{stream_event}'")
                    CACHE_LOOKUP_COUNT.labels(result='hit').inc()
                    TRANSACTION_COUNT.labels(status='success_cache').inc()
                    return result
            except Exception as e:
                print(f"⚠️ Cache read anomaly ignored: {str(e)}")

        try:
            print(f"📥 [KAFKA-CONSUMER] Cache miss. Processing partition record payload: '{stream_event}'")
            CACHE_LOOKUP_COUNT.labels(result='miss').inc()
            result = await loop.run_in_executor(pool, _cpu_bound_symbolic_task, stream_event)
            print(f"  |-- Invariant Intact: {result.get('volume_invariant_holds')}\n")
            if redis and result:
                asyncio.create_task(redis.setex(cache_key, 3600, json.dumps(result)))
            TRANSACTION_COUNT.labels(status='success_compute').inc()
            return result
        except Exception as e:
            print(f"❌ Worker process execution fault: {str(e)}", file=sys.stderr)
            TRANSACTION_COUNT.labels(status='failure').inc()
            return None

async def mock_kafka_stream_producer(kafka_topic_buffer: asyncio.Queue):
    """Simulates a continuous high-velocity distributed transaction queue broker stream source."""
    expressions_pool = ["x + 5", "150", "y * 2", "balance_a - 200", "50"]
    while True:
        simulated_payload = random.choice(expressions_pool)
        await kafka_topic_buffer.put(simulated_payload)
        await asyncio.sleep(random.uniform(0.1, 0.4))

async def mock_kafka_stream_consumer(kafka_topic_buffer: asyncio.Queue):
    """Infinite real-time streaming event consumption interface loop."""
    while True:
        stream_event = await kafka_topic_buffer.get()
        asyncio.create_task(process_stream_transaction(stream_event))
        kafka_topic_buffer.task_done()

async def main():
    """System entry point for real-time distributed stream cluster testing."""
    print("📊 [MONITORING] Initializing native Prometheus exporter listener pool on port 8000...")
    start_http_server(8000)
    print(f"⚡ Launching Ultra-Low Latency uvloop Engine across {os.cpu_count()} Worker Processes...")
    kafka_topic_buffer = asyncio.Queue(maxsize=100)
    producer_task = asyncio.create_task(mock_kafka_stream_producer(kafka_topic_buffer))
    consumer_task = asyncio.create_task(mock_kafka_stream_consumer(kafka_topic_buffer))
    try:
        await asyncio.gather(producer_task, consumer_task)
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    try:
        import uvloop
        uvloop.install()
    except ImportError:
        pass
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Kafka stream consumer. Terminal loop interrupted.")
    finally:
        if _PROCESS_POOL:
            _PROCESS_POOL.shutdown(wait=True)
