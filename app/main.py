"""
F1 Race Outcome Predictor - Main API Server
A cutting-edge machine learning platform for F1 predictions
"""

import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from dotenv import load_dotenv

from app.core.config import settings
from app.api.v1.api import api_router
from app.core.database import init_db
from app.core.logging import setup_logging

# Load environment variables
load_dotenv()

# Setup logging
logger = setup_logging()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("🏎️ Starting F1 Race Outcome Predictor API...")
    
    # Initialize database
    try:
        await init_db()
        logger.info("✅ Database initialized successfully")
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise
    
    # Load ML models
    try:
        from app.ml.model_manager import ModelManager
        model_manager = ModelManager()
        await model_manager.load_models()
        app.state.model_manager = model_manager
        logger.info("✅ ML models loaded successfully")
    except Exception as e:
        logger.error(f"❌ Model loading failed: {e}")
    
    logger.info("🚀 F1 Predictor API is ready!")
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down F1 Predictor API...")

# Create FastAPI application
app = FastAPI(
    title="F1 Race Outcome Predictor API",
    description="A cutting-edge machine learning platform that transforms the F1 fan experience through real-time predictions, interactive features, and data-driven race analytics.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=f"/api/{settings.API_VERSION}")

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🏎️ F1 Race Outcome Predictor API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": "2024-01-01T00:00:00Z",
        "version": "1.0.0"
    }

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": "2024-01-01T00:00:00Z"
        }
    )

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
