import asyncio
import time
import random
from locust import User, task, between, events
from src.infrastructure.orchestrator import process_stream_transaction

# Pool of expressions ranging from quick execution constants to complex multi-variable algebra equations
EXPRESSIONS_STRESS_POOL = [
    "x + 5", 
    "150", 
    "y * 2", 
    "balance_a - 200", 
    "50",
    "x**2 + y**2 - balance_a",
    "(z * 4) + x - 1000"
]

class SymbolicEngineStressUser(User):
    """
    Custom Asynchronous Locust User configured to bypass default HTTP mechanics 
    and directly benchmark the core processing pool concurrency loop limits.
    """
    # Simulate users firing transactions dynamically with low pacing delays (0.01s - 0.05s)
    wait_time = between(0.01, 0.05)

    def on_start(self):
        """Pre-flight setup: Grab or initialize the asynchronous event execution loop policy context."""
        try:
            self.async_loop = asyncio.get_event_loop()
        except RuntimeError:
            self.async_loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.async_loop)

    @task
    def stress_test_transaction_pipeline(self):
        """Simulates a concurrent user injecting variable math payloads directly into the processor core."""
        payload = random.choice(EXPRESSIONS_STRESS_POOL)
        start_time = time.perf_counter()
        
        try:
            # Execute the non-blocking process worker pool task through the active async event loop
            future = asyncio.run_coroutine_threadsafe(
                process_stream_transaction(payload), 
                self.async_loop
            )
            # Block the virtual locust runner thread until the process worker task evaluates completely
            result = future.result(timeout=5.0)
            
            total_latency = (time.perf_counter() - start_time) * 1000 # Convert execution speed to milliseconds
            
            if result and result.get("volume_invariant_holds") is True:
                # Log successful transaction resolution metrics back to the central master dashboard registry
                events.request.fire(
                    request_type="ASYNC_PROCESS",
                    name="verify_transaction_safety",
                    response_time=total_latency,
                    response_length=0,
                    exception=None
                )
            else:
                raise ValueError("Engine returned empty matrix context properties or broken validation state.")
                
        except Exception as e:
            total_latency = (time.perf_counter() - start_time) * 1000
            # Record execution fault metrics, timeouts, or processor saturation points
            events.request.fire(
                request_type="ASYNC_PROCESS",
                name="verify_transaction_safety",
                response_time=total_latency,
                response_length=0,
                exception=e
            )
