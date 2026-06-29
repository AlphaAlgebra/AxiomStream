import asyncio
from concurrent.futures import ProcessPoolExecutor
import sympy

# =====================================================================
# 1. FIXED: Moved worker completely OUTSIDE the class.
# This makes it a pure top-level function that Python can safely pickle.
# =====================================================================
def _solve_symbolic_worker(expression_str: str, variable_str: str) -> str:
    """
    Worker function executed inside the isolated process pool.
    Input arguments must be pure, picklable primitive types (strings).
    """
    try:
        # Reconstruct the SymPy expressions within the worker's isolated memory
        x = sympy.Symbol(variable_str)
        expr = sympy.sympify(expression_str)
        
        # Perform the heavy CPU-bound computation
        result = sympy.solve(expr, x)
        
        # Convert back to a primitive string before passing back across the process boundary
        return str(result)
    except Exception as e:
        return f"Error processing equation: {str(e)}"


class AxiomStreamEngine:
    def __init__(self, max_workers: int = 4):
        # Dedicated process executor pool for handling heavy mathematical calculations
        self.executor = ProcessPoolExecutor(max_workers=max_workers)

    # =====================================================================
    # 2. FIXED: Master Async Pipeline Execution
    # =====================================================================
    async def process_batch(self, batch: list[dict]) -> list[str]:
        """
        Asynchronously handles incoming stream batches without blocking the event loop.
        """
        loop = asyncio.get_running_loop()
        tasks = []

        for item in batch:
            # FIXED: Extract data as primitive strings before sending to the executor
            expr_str = str(item.get("expression", ""))
            var_str = str(item.get("symbol", "x"))

            # Pass the pure top-level worker function instead of an instance method
            task = loop.run_in_executor(
                self.executor,
                _solve_symbolic_worker,
                expr_str,
                var_str
            )
            tasks.append(task)

        # Execute all calculations in parallel across CPU cores non-blockingly
        return await asyncio.gather(*tasks)

    def shutdown(self):
        """Cleanly releases cluster resources upon completion."""
        self.executor.shutdown(wait=True)
