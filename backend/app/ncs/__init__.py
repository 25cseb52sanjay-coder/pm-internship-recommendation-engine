"""
NCS (National Career Service) Integration Module
Isolated package for National Career Service India internship data models, schemas, and API connectors.
"""

from app.ncs.schemas import NCSInternshipSchema
from app.ncs.connector import NCSConnector
from app.ncs.service import NCSService
from app.ncs.sync_service import NCSSyncService

__all__ = ["NCSInternshipSchema", "NCSConnector", "NCSService", "NCSSyncService"]
