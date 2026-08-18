from app.ingestion.routers.admin_ingestion import router as admin_ingestion_router
from app.ingestion.routers.ingestion_status import router as ingestion_status_router

__all__ = [
    "admin_ingestion_router",
    "ingestion_status_router"
]
