import pytest
import requests
from src.infrastructure.master_pipeline import ingest_fedramp_data

def test_network_timeout_fallback(monkeypatch):
    """
    Advanced Assert: Simulates high network latency where DNS resolves 
    but the HTTP connection times out, ensuring fallback activation.
    """
    
    # 1. Define a mock function that simulates a requests Timeout exception
    def mock_requests_get_timeout(*args, **kwargs):
        raise requests.exceptions.Timeout("Connection timed out due to high target latency.")

    # 2. Intercept requests.get to simulate the slow I/O connection phase
    monkeypatch.setattr(requests, "get", mock_requests_get_timeout)

    # 3. Execute the data ingestion loop under simulated high latency
    fallback_payload = ingest_fedramp_data()

    # 4. Verify data structure integrity invariants remain valid
    assert fallback_payload is not None, "Fallback core failed to generate data matrices on timeout."
    assert isinstance(fallback_payload, list), "Data contract mismatch: Payload must remain a list."
    assert len(fallback_payload) == 3, "Payload shape altered under network timeout conditions."

    # 5. Confirm that our fallback providers are cleanly compiled into memory
    providers = [item["Cloud Provider"] for item in fallback_payload]
    assert "Amazon Web Services" in providers
    assert "Microsoft" in providers
    assert "Google" in providers
