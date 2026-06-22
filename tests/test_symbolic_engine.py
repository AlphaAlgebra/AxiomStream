import socket
import pytest
from src.infrastructure.master_pipeline import ingest_fedramp_data

def test_dns_resolution_failure_fallback(monkeypatch):
    """
    Advanced Assert: Verifies that the orchestration loop handles 
    system-level DNS gaierrors cleanly and activates localized memory buffers.
    """
    
    # 1. Define a faulty mock function that raises a native network resolution failure
    def mock_gethostbyname_exception(host):
        raise socket.gaierror(-5, "Name or service not known")

    # 2. Intercept the live socket configuration using monkeypatch
    # This prevents the test runner from reaching out to external GitHub networks
    monkeypatch.setattr(socket, "gethostbyname", mock_gethostbyname_exception)

    # 3. Execute the function under a simulated network drop
    fallback_payload = ingest_fedramp_data()

    # 4. Assert structural integrity and compliance ledger contracts
    assert fallback_payload is not None, "Fallback core failed to return a valid payload matrix."
    assert isinstance(fallback_payload, list), "Data structure contract mismatch: Expected a list type."
    assert len(fallback_payload) == 3, "Payload shape modified: Fallback must account for exactly 3 cloud providers."

    # 5. Assert value verification targets to ensure localized records are valid
    providers = [item["Cloud Provider"] for item in fallback_payload]
    assert "Amazon Web Services" in providers, "AWS cloud compliance record missing from offline buffer."
    assert "Microsoft" in providers, "Azure cloud compliance record missing from offline buffer."
    assert "Google" in providers, "Google workspace record missing from offline buffer."
