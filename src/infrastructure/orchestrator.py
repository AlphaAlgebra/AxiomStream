import asyncio
import os
import sys
import random
from concurrent.futures import ProcessPoolExecutor
from src.engine.symbolic_solver import SymbolicStateVerifier

# Global process pool container to optimize hardware worker context lifetimes
_PROCESS_POOL: ProcessPoolExecutor = None

def get_compute_pool() -> ProcessPoolExecutor:
    """Initializes or returns a cached multi-core execution process pool layout."""
    global _PROCESS_POOL
    if _PROCESS_POOL is None:
        max_workers = os.cpu_count() or 2
        _PROCESS_POOL = ProcessPoolExecutor(max_workers=max_workers)
    return _PROCESS_POOL

def _cpu_bound_symbolic_task(expression: str) -> dict:
    """
    Isolated computational worker callback. Runs strictly inside an independent OS process 
    to completely bypass the Python Global Interpreter Lock (GIL).
    """
    verifier = SymbolicStateVerifier()
    return verifier.verify_transaction_safety(expression)

async def process_stream_transaction(stream_event: str):
    """
    Asynchronous transaction processor. Awaits process-pool completion without stalling
    the concurrent background ingestion loops.
    """
    loop = asyncio.get_running_loop()
    pool = get_compute_pool()
    
    try:
        print(f"📥 [KAFKA-CONSUMER] Processing partition record payload: '{stream_event}'")
        result = await loop.run_in_executor(pool, _cpu_bound_symbolic_task, stream_event)
        
        print(f"  |-- Invariant Intact: {result.get('volume_invariant_holds')}")
        print(f"  |-- Hazard Alert: {result.get('overdraft_risk_detected')}")
        print(f"  |-- Solver Boundary Condition: {result.get('boundary_hazards')}\n")
        return result
    except Exception as e:
        print(f"❌ Worker process execution fault: {str(e)}", file=sys.stderr)
        return None

async def mock_kafka_stream_producer(kafka_topic_buffer: asyncio.Queue):
    """
    Simulates a high-velocity upstream Apache Kafka broker pushing continuous
    distributed transaction state expressions down the data pipeline.
    """
    expressions_pool = ["x + 5", "150", "y * 2", "balance_a - 200", "50"]
    print("📢 [KAFKA-BROKER] Connection established. Initializing transaction streams...")
    
    while True:
        simulated_payload = random.choice(expressions_pool)
        await kafka_topic_buffer.put(simulated_payload)
        await asyncio.sleep(random.uniform(0.1, 0.5))

async def mock_kafka_stream_consumer(kafka_topic_buffer: asyncio.Queue):
    """
    An infinite asynchronous streaming event loop running on top of uvloop's high-speed
    libuv layer to handle concurrent task worker allocations instantly.
    """
    print("🎧 [KAFKA-CONSUMER] Subscribed to validation topic stream. Waiting for offsets...")
    while True:
        stream_event = await kafka_topic_buffer.get()
        asyncio.create_task(process_stream_transaction(stream_event))
        kafka_topic_buffer.task_done()

async def main():
    """System entry point for real-time distributed stream cluster testing."""
    print(f"⚡ Launching Ultra-Low Latency uvloop Engine across {os.cpu_count()} Worker Processes...")
    
    kafka_topic_buffer = asyncio.Queue(maxsize=100)
    
    producer_task = asyncio.create_task(mock_kafka_stream_producer(kafka_topic_buffer))
    consumer_task = asyncio.create_task(mock_kafka_stream_consumer(kafka_topic_buffer))
    
    try:
        await asyncio.gather(producer_task, consumer_task)
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    # --- ENTERPRISE ARTIFACT: DYNAMICALLY INJECT ULTRA-LOW LATENCY UVLOOP RUNTIME ---
    try:
        import uvloop
        # Install uvloop as the global default asyncio event loop policy
        uvloop.install()
        print("🚀 [ENGINE-INFRA] Successfully initialized high-performance libuv core wrapper policy.")
    except ImportError:
        print("⚠️ [ENGINE-INFRA] uvloop library not found. Falling back to native system asyncio loop runtime.")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Shutting down Kafka stream consumer. Terminal loop interrupted.")
    finally:
        if _PROCESS_POOL:
            _PROCESS_POOL.shutdown(wait=True)
