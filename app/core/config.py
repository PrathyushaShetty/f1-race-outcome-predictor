"""
Configuration settings for F1 Race Outcome Predictor
"""

import os
from typing import List, Optional
from pydantic import BaseSettings, validator


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    F1_API_KEY: Optional[str] = None
    WEATHER_API_KEY: Optional[str] = None
    ERGAST_API_BASE_URL: str = "http://ergast.com/api/f1"
    
    # Database Configuration
    DATABASE_URL: str = "postgresql://username:password@localhost:5432/f1_predictor"
    DATABASE_HOST: str = "localhost"
    DATABASE_PORT: int = 5432
    DATABASE_NAME: str = "f1_predictor"
    DATABASE_USER: str = "username"
    DATABASE_PASSWORD: str = "password"
    
    # Redis Configuration
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    
    # Model Configuration
    MODEL_UPDATE_INTERVAL: int = 3600
    PREDICTION_CONFIDENCE_THRESHOLD: float = 0.75
    MODEL_RETRAIN_SCHEDULE: str = "0 2 * * *"
    
    # Application Settings
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "your_secret_key_here"
    API_VERSION: str = "v1"
    MAX_WORKERS: int = 4
    
    # External APIs
    FASTF1_CACHE_DIR: str = "./cache/fastf1"
    ERGAST_CACHE_ENABLED: bool = True
    WEATHER_UPDATE_INTERVAL: int = 300
    
    # WebSocket Configuration
    WS_HOST: str = "0.0.0.0"
    WS_PORT: int = 8001
    
    # API Server Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    
    # Prediction Engine Settings
    LIVE_PREDICTION_INTERVAL: int = 30
    RACE_DATA_REFRESH_RATE: int = 10
    
    # Security
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:8080"]
    JWT_SECRET_KEY: str = "your_jwt_secret_key_here"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24
    
    @validator("CORS_ORIGINS", pre=True)
    def assemble_cors_origins(cls, v):
        if isinstance(v, str):
            return [i.strip() for i in v.split(",")]
        return v
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Create settings instance
settings = Settings()
