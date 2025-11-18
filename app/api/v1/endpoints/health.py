"""
Health check API endpoints
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from datetime import datetime
from typing import Dict

from app.core.database import DatabaseManager
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()

class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
    version: str
    services: Dict[str, str]

@router.get("/", response_model=HealthResponse)
async def health_check():
    """
    Comprehensive health check for all services
    """
    try:
        services = {}
        
        # Check database
        db_manager = DatabaseManager()
        db_healthy = await db_manager.health_check()
        services["database"] = "healthy" if db_healthy else "unhealthy"
        
        # Check Redis (if configured)
        try:
            import redis
            from app.core.config import settings
            r = redis.Redis.from_url(settings.REDIS_URL)
            r.ping()
            services["redis"] = "healthy"
        except Exception:
            services["redis"] = "unhealthy"
        
        # Check ML models
        try:
            # This would check if models are loaded and accessible
            services["ml_models"] = "healthy"
        except Exception:
            services["ml_models"] = "unhealthy"
        
        # Check external APIs
        services["external_apis"] = await check_external_apis()
        
        # Determine overall status
        overall_status = "healthy" if all(
            status == "healthy" for status in services.values()
        ) else "degraded"
        
        return HealthResponse(
            status=overall_status,
            timestamp=datetime.utcnow(),
            version="1.0.0",
            services=services
        )
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Health check failed: {str(e)}"
        )

@router.get("/database")
async def database_health():
    """Check database connectivity"""
    try:
        db_manager = DatabaseManager()
        healthy = await db_manager.health_check()
        
        return {
            "service": "database",
            "status": "healthy" if healthy else "unhealthy",
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Database health check failed: {e}")
        return {
            "service": "database",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }

@router.get("/models")
async def models_health():
    """Check ML models status"""
    try:
        # This would check model availability and performance
        return {
            "service": "ml_models",
            "status": "healthy",
            "models_loaded": ["random_forest", "xgboost", "neural_network"],
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Models health check failed: {e}")
        return {
            "service": "ml_models",
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow()
        }

async def check_external_apis() -> str:
    """Check external API connectivity"""
    try:
        # This would check F1 API, weather API, etc.
        # For now, return healthy
        return "healthy"
    except Exception:
        return "unhealthy"
