import asyncio
import os
import sys
from concurrent.futures import ProcessPoolExecutor
from src.engine.symbolic_solver import SymbolicStateVerifier

# Global process pool initializer to reuse worker resources efficiently
_PROCESS_POOL: ProcessPoolExecutor = None

def get_compute_pool() -> ProcessPoolExecutor:
    """Initializes or returns a cached multi-core execution process pool layout."""
    global _PROCESS_POOL
    if _PROCESS_POOL is None:
        # Dynamically allocate exactly 1 worker per physical/logical processor core
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

async def stream_transaction_orchestrator(stream_event: str):
    """
    Asynchronous event lifecycle handler. Offloads heavy equations without blocking
    the non-blocking network reception loop.
    """
    loop = asyncio.get_running_loop()
    pool = get_compute_pool()
    
    try:
        # Pass the task to the compute pool while cleanly awaiting the result asynchronously
        print(f"📥 Ingested stream transaction payload expression: '{stream_event}'")
        result = await loop.run_in_executor(pool, _cpu_bound_symbolic_task, stream_event)
        
        print(f" |-- Volume Invariant Holds: {result.get('volume_invariant_holds')}")
        print(f" |-- State Risk Alert Status: {result.get('overdraft_risk_detected')}")
        print(f" |-- Safety Boundary Rules: {result.get('boundary_hazards')}\n")
        return result
    except Exception as e:
        print(f"❌ Structural crash inside computational worker node: {str(e)}", file=sys.stderr)
        return None

async def main():
    """Simulated real-time streaming batch execution pipeline entrypoint."""
    print(f"⚡ Launching Async Orchestrator Framework via {os.cpu_count()} CPU Process Workers...")
    
    # Simulating a high-velocity ingress stream batch
    mock_event_stream = [
        "x + 5",
        "150",
        "y * 2",
        "balance_a - 200",
        "50"
    ]
    
    # Process the incoming streams concurrently using high-performance task scheduling
    tasks = [asyncio.create_task(stream_transaction_orchestrator(event)) for event in mock_event_stream]
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Execution pool termination sequence completed.")
    finally:
        if _PROCESS_POOL:
            _PROCESS_POOL.shutdown(wait=True)
