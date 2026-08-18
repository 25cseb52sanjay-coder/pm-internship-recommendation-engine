import os
import logging
from typing import Dict, Optional, Tuple, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class AdzunaConfig:
    """
    Secure configuration handler for Adzuna REST API credentials.
    Reads ADZUNA_APP_ID and ADZUNA_APP_KEY directly from environment variables.
    Credentials are never hardcoded or exposed to the frontend.
    """

    @classmethod
    def get_app_id(cls) -> Optional[str]:
        """Returns the configured ADZUNA_APP_ID from environment settings."""
        app_id = os.getenv("ADZUNA_APP_ID") or settings.ADZUNA_APP_ID
        if app_id:
            return app_id.strip()
        return None

    @classmethod
    def get_app_key(cls) -> Optional[str]:
        """Returns the configured ADZUNA_APP_KEY from environment settings."""
        app_key = os.getenv("ADZUNA_APP_KEY") or settings.ADZUNA_APP_KEY
        if app_key:
            return app_key.strip()
        return None

    @classmethod
    def get_credentials(cls) -> Tuple[Optional[str], Optional[str]]:
        """
        Returns (app_id, app_key) tuple securely from environment settings.
        """
        return cls.get_app_id(), cls.get_app_key()

    @classmethod
    def is_configured(cls) -> bool:
        """
        Checks whether both ADZUNA_APP_ID and ADZUNA_APP_KEY environment variables are present and non-empty.
        """
        app_id, app_key = cls.get_credentials()
        return bool(app_id and app_key)

    @classmethod
    def get_auth_status(cls) -> Dict[str, Any]:
        """
        Returns non-sensitive metadata regarding Adzuna API authentication status.
        Does NOT expose raw keys or secrets.
        """
        app_id, app_key = cls.get_credentials()
        configured = bool(app_id and app_key)
        
        return {
            "source_name": "Adzuna Job Board API",
            "is_configured": configured,
            "has_app_id": bool(app_id),
            "has_app_key": bool(app_key),
            "app_id_masked": f"{app_id[:4]}***" if app_id and len(app_id) >= 4 else "NOT_CONFIGURED",
            "auth_type": "APP_ID_AND_APP_KEY",
            "base_url": "https://api.adzuna.com/v1/api/jobs"
        }

def get_adzuna_credentials() -> Tuple[Optional[str], Optional[str]]:
    return AdzunaConfig.get_credentials()

def is_adzuna_configured() -> bool:
    return AdzunaConfig.is_configured()
