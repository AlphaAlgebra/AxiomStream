import socket
import pytest
import requests
from src.infrastructure.master_pipeline import ingest_fedramp_data
from src.engine.symbolic_solver import SymbolicStateVerifier

def test_dns_resolution_failure_fallback(monkeypatch):
    def mock_gethostbyname_exception(host):
        raise socket.gaierror(-5, "Name or service not known")
    monkeypatch.setattr(socket, "gethostbyname", mock_gethostbyname_exception)
    fallback_payload = ingest_fedramp_data()
    assert fallback_payload is not None
    assert isinstance(fallback_payload, list)
    assert len(fallback_payload) == 3

def test_network_timeout_fallback(monkeypatch):
    def mock_requests_get_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout("Connection timed out due to high target latency.")
    monkeypatch.setattr(requests, "get", mock_requests_get_timeout)
    fallback_payload = ingest_fedramp_data()
    assert fallback_payload is not None
    assert isinstance(fallback_payload, list)
    assert len(fallback_payload) == 3

def test_network_to_verifier_integration(monkeypatch):
    def mock_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout("Simulated latency check.")
    monkeypatch.setattr(requests, "get", mock_timeout)
    compliance_data = ingest_fedramp_data()
    assert isinstance(compliance_data, list), "Data ingestion step failed."
    verifier = SymbolicStateVerifier()
    verification_result = verifier.verify_transaction_safety("x + 5")
    assert "volume_invariant_holds" in verification_result
    assert "boundary_hazards" in verification_result
    assert verification_result["volume_invariant_holds"] is True

@pytest.mark.parametrize(
    "dynamic_expression, expected_alert, rule_key",
    [
        ("x + 5", True, "x > balance_a - 5"),
        ("150", False, "None"),
        ("y * 2", True, "y > balance_a/2"),
        ("balance_a - 200", True, "False"),
        ("50", False, "None")
    ]
)
def test_dynamic_equations_integration(monkeypatch, dynamic_expression, expected_alert, rule_key):
    def mock_latency_drop(*args, **kwargs):
        raise requests.exceptions.Timeout("Simulated latency drops.")
    monkeypatch.setattr(requests, "get", mock_latency_drop)
    
    compliance_data = ingest_fedramp_data()
    verifier = SymbolicStateVerifier()
    
    expression_to_test = "x + 5"
    exp_result = verifier.verify_expression(expression_to_test, compliance_data)
    assert "Volume Invariant Intact" in exp_result
    assert "Safety Boundary Condition" in exp_result
    assert exp_result["Volume Invariant Intact"] is True
    
    verification_result = verifier.verify_transaction_safety(dynamic_expression)
    assert verification_result["volume_invariant_holds"] is True
    assert verification_result["overdraft_risk_detected"] == expected_alert
    assert rule_key in str(verification_result["boundary_hazards"])
