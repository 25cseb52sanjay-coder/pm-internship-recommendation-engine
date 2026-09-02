import os
import sys

sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))

from app.jobvetta.config import JobvettaConfig
from app.jobvetta.connector import JobvettaConnector

def test_jobvetta_config_missing_key():
    """Verify that missing JOBVETTA_API_KEY marks connector status as NOT_CONFIGURED without crashing backend."""
    orig_key = os.environ.get("JOBVETTA_API_KEY")
    try:
        if "JOBVETTA_API_KEY" in os.environ:
            del os.environ["JOBVETTA_API_KEY"]
        connector = JobvettaConnector(api_key=None)
        assert connector.authorization_status == "NOT_CONFIGURED"
        assert not connector.check_authorization()
    finally:
        if orig_key:
            os.environ["JOBVETTA_API_KEY"] = orig_key

def test_jobvetta_config_with_key():
    """Verify that valid JOBVETTA_API_KEY initializes connector status as AUTHORIZED."""
    connector = JobvettaConnector(api_key="test_secret_jobvetta_key_123")
    assert connector.authorization_status == "AUTHORIZED"
    assert connector.check_authorization()
    headers = connector.get_headers()
    assert headers["Authorization"] == "Bearer test_secret_jobvetta_key_123"
