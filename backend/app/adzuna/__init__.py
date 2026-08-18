"""
Adzuna Job Board Integration Module
Official REST API documentation: https://developer.adzuna.com/overview
"""

from app.adzuna.config import get_adzuna_credentials, is_adzuna_configured, AdzunaConfig
from app.adzuna.connector import AdzunaConnector
from app.adzuna.service import AdzunaService
from app.adzuna.classifier import classify_adzuna_opportunity
from app.adzuna.sync_service import AdzunaSyncService

__all__ = [
    "get_adzuna_credentials",
    "is_adzuna_configured",
    "AdzunaConfig",
    "AdzunaConnector",
    "AdzunaService",
    "classify_adzuna_opportunity",
    "AdzunaSyncService"
]
