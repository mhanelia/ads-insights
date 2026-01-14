"""Health check endpoint."""

from datetime import datetime

from fastapi import APIRouter

from app.config import get_settings

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """
    Health check endpoint.
    
    Returns basic application status and configuration info.
    """
    settings = get_settings()
    
    return {
        "status": "healthy",
        "version": settings.app_version,
        "timestamp": datetime.utcnow().isoformat(),
        "llm_provider": settings.llm_provider.value,
        "llm_configured": settings.is_llm_configured(),
    }
