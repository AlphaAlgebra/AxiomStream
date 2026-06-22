import pytest
import requests
from src.infrastructure.master_pipeline import ingest_fedramp_data
from src.engine.symbolic_solver import SymbolicStateVerifier

def test_network_to_verifier_integration(monkeypatch):
    """
    Integration Assert: Verifies data pipeline integration from the 
    network fallback layer directly into the SymbolicStateVerifier engine.
    """
    # 1. Force a timeout to guarantee the ingestion pipeline drops to fallback buffers
    def mock_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout("Simulated latency check.")
    
    monkeypatch.setattr(requests, "get", mock_timeout)

    # 2. Step 1 of Integration: Fetch the compliance data payload matrix
    compliance_data = ingest_fedramp_data()
    assert isinstance(compliance_data, list), "Data ingestion step failed."

    # 3. Step 2 of Integration: Initialize your formal verifier with the network output
    # We verify the engine can parse the real strings provided by the fallback buffer
    verifier = SymbolicStateVerifier()
    
    # 4. Step 3 of Integration: Feed ingestion components into calculation loops
    # Test checking a streaming balance boundary using the data context
    expression_to_test = "x + 5"
    verification_result = verifier.verify_expression(expression_to_test, compliance_data)

    # 5. Core End-to-End System Assertions
    assert "Volume Invariant Intact" in verification_result
    assert "Safety Boundary Condition" in verification_result
    assert verification_result["Volume Invariant Intact"] is True, "Mathematical invariant broken during data pipeline transit."
