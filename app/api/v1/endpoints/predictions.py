"""
Prediction API endpoints
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel
from datetime import datetime

from app.ml.predictor import RacePredictor
from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()

# Pydantic models for request/response
class PreRacePredictionResponse(BaseModel):
    race_id: str
    predictions: Dict
    confidence: float
    timestamp: datetime
    weather_conditions: Optional[Dict] = None
    track_info: Optional[Dict] = None

class PodiumPredictionResponse(BaseModel):
    race_id: str
    podium_probabilities: List[Dict]
    timestamp: datetime

class LivePredictionResponse(BaseModel):
    race_id: str
    current_lap: int
    live_probabilities: Dict
    position_changes: List[Dict]
    timestamp: datetime

@router.get("/pre-race/{race_id}", response_model=PreRacePredictionResponse)
async def get_pre_race_predictions(race_id: str):
    """
    Get pre-race predictions for a specific race
    
    - **race_id**: Race identifier (e.g., 'bahrain-2024', 'monaco-2024')
    """
    try:
        predictor = RacePredictor()
        
        # Load race data
        race_data = await predictor.load_race_data(race_id)
        
        # Generate predictions
        predictions = await predictor.predict_race_outcome(race_data)
        
        # Get weather data
        weather_data = await predictor.get_weather_forecast(race_id)
        
        # Get track information
        track_info = await predictor.get_track_characteristics(race_id)
        
        return PreRacePredictionResponse(
            race_id=race_id,
            predictions=predictions,
            confidence=predictions.get('confidence', 0.0),
            timestamp=datetime.utcnow(),
            weather_conditions=weather_data,
            track_info=track_info
        )
        
    except Exception as e:
        logger.error(f"Pre-race prediction failed for {race_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate pre-race predictions: {str(e)}"
        )

@router.get("/podium/{race_id}", response_model=PodiumPredictionResponse)
async def get_podium_probabilities(race_id: str):
    """
    Get podium finish probabilities for drivers
    
    - **race_id**: Race identifier
    """
    try:
        predictor = RacePredictor()
        
        # Generate podium probabilities
        podium_probs = await predictor.predict_podium_probabilities(race_id)
        
        return PodiumPredictionResponse(
            race_id=race_id,
            podium_probabilities=podium_probs,
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Podium prediction failed for {race_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate podium predictions: {str(e)}"
        )

@router.get("/live/{race_id}", response_model=LivePredictionResponse)
async def get_live_predictions(race_id: str, lap: Optional[int] = None):
    """
    Get live race predictions during an ongoing race
    
    - **race_id**: Race identifier
    - **lap**: Specific lap number (optional, defaults to current lap)
    """
    try:
        predictor = RacePredictor()
        
        # Get live race data
        live_data = await predictor.get_live_race_data(race_id, lap)
        
        # Generate live predictions
        live_predictions = await predictor.predict_live_race_outcome(live_data)
        
        return LivePredictionResponse(
            race_id=race_id,
            current_lap=live_data.get('current_lap', 0),
            live_probabilities=live_predictions.get('probabilities', {}),
            position_changes=live_predictions.get('position_changes', []),
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Live prediction failed for {race_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate live predictions: {str(e)}"
        )

@router.post("/update-models")
async def trigger_model_update(background_tasks: BackgroundTasks):
    """
    Trigger model retraining and updates
    """
    try:
        background_tasks.add_task(update_models_background)
        return {"message": "Model update triggered successfully"}
        
    except Exception as e:
        logger.error(f"Model update trigger failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to trigger model update: {str(e)}"
        )

async def update_models_background():
    """Background task for model updates"""
    try:
        from app.ml.model_manager import ModelManager
        model_manager = ModelManager()
        await model_manager.retrain_models()
        logger.info("✅ Models updated successfully")
    except Exception as e:
        logger.error(f"❌ Model update failed: {e}")
