"""
API v1 router configuration
"""

from fastapi import APIRouter
from app.api.v1.endpoints import predictions, fans, health

api_router = APIRouter()

# Include prediction endpoints
api_router.include_router(
    predictions.router,
    prefix="/predictions",
    tags=["predictions"]
)

# Include fan interaction endpoints
api_router.include_router(
    fans.router,
    prefix="/fans",
    tags=["fans"]
)

# Include health endpoints
api_router.include_router(
    health.router,
    prefix="/health",
    tags=["health"]
)
