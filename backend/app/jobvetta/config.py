import os
from typing import Tuple, Optional
from app.core.config import settings

class JobvettaConfig:
    """
    Configuration helper for Jobvetta API authorization credentials.
    Reads JOBVETTA_API_KEY and JOBVETTA_API_BASE_URL server-side only.
    """

    @staticmethod
    def get_credentials() -> Tuple[Optional[str], str]:
        """
        Returns (api_key, base_url).
        Reads from settings / environment securely without exposing credentials to client.
        """
        api_key = settings.JOBVETTA_API_KEY or os.getenv("JOBVETTA_API_KEY")
        base_url = settings.JOBVETTA_API_BASE_URL or os.getenv("JOBVETTA_API_BASE_URL", "https://api.jobvetta.com/v1")
        return api_key, base_url

    @staticmethod
    def is_configured() -> bool:
        """Checks if Jobvetta API authorization credentials are configured."""
        api_key, _ = JobvettaConfig.get_credentials()
        return bool(api_key and api_key.strip())
