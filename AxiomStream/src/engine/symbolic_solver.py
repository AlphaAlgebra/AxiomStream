import sympy as sp


class SymbolicStateVerifier:
    def __init__(self):
        self.balance_a, self.balance_b = sp.symbols("balance_a balance_b")
        self.initial_total = 1000
        self.invariant_total_funds = sp.Eq(
            self.balance_a + self.balance_b, self.initial_total
        )

    def verify_transaction_safety(self, transfer_amount_expr: str) -> dict:
        k = sp.sympify(transfer_amount_expr)

        # 1. Structural Invariant: Ensure volume preservation
        new_a = self.balance_a - k
        new_b = self.balance_b + k
        new_total_funds = sp.Eq(new_a + new_b, self.initial_total)
        is_volume_preserved = sp.simplify(new_total_funds) == sp.simplify(
            self.invariant_total_funds
        )

        # 2. Risk Detection: Check if the transfer expression itself can be negative
        # or forces balance_a below zero by finding its lower bound boundaries.
        free_symbols = k.free_symbols
        hazard_found = False
        hazard_msg = "None"

        if free_symbols:
            # Check if there's any condition where transfer expression k > balance_a
            overdraft_condition = k > self.balance_a
            # Evaluate if the expression could cause an unexpected state step
            try:
                # Isolate boundaries based on the free variables (e.g., x)
                target_sym = list(free_symbols)[0]
                hazard_solutions = sp.solve(overdraft_condition, target_sym)
                hazard_found = True
                hazard_msg = f"Potential overdraft if state matches condition: {hazard_solutions}"
            except Exception:
                # Fallback check: if expression is too complex, flag as an unverified boundary risk
                hazard_found = True
                hazard_msg = f"Complex dynamic expression unverified: contains free symbols {free_symbols}"
        else:
            # Static value check
            if float(k) > self.initial_total or float(k) < 0:
                hazard_found = True
                hazard_msg = f"Static value {k} violates systemic safety constraints."

        return {
            "volume_invariant_holds": bool(is_volume_preserved),
            "overdraft_risk_detected": hazard_found,
            "boundary_hazards": hazard_msg,
        }


if __name__ == "__main__":
    verifier = SymbolicStateVerifier()
    print("Evaluating dynamic symbolic transfer 'x + 5':")
    result = verifier.verify_transaction_safety("x + 5")
    print(f"-> Volume Preserved: {result['volume_invariant_holds']}")
    print(f"-> Risk State Analysis: {result['boundary_hazards']}")
