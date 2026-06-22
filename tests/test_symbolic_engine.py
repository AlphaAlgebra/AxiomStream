import pytest
from src.engine.symbolic_solver import SymbolicStateVerifier

@pytest.fixture
def verifier():
    return SymbolicStateVerifier()

def test_static_safe_transaction(verifier):
    """Asserts that standard valid static amounts do not trigger alerts."""
    result = verifier.verify_transaction_safety("100")
    assert result["volume_invariant_holds"] is True
    assert result["overdraft_risk_detected"] is False

def test_static_overdraft_hazard(verifier):
    """Asserts that static boundaries exceeding total pool funds are caught."""
    result = verifier.verify_transaction_safety("1500")
    assert result["volume_invariant_holds"] is True
    assert result["overdraft_risk_detected"] is True

def test_dynamic_algebraic_hazard(verifier):
    """Asserts that algebraic constraints are isolated correctly for variables."""
    result = verifier.verify_transaction_safety("x + 10")
    assert result["volume_invariant_holds"] is True
    assert result["overdraft_risk_detected"] is True
    assert "x > balance_a - 10" in result["boundary_hazards"]
