"""
Fan interaction API endpoints
"""

from typing import Dict, List, Optional
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime

from app.core.logging import setup_logging

logger = setup_logging()
router = APIRouter()

# Pydantic models
class FanPrediction(BaseModel):
    user_id: str
    race_id: str
    winner_prediction: str
    podium_predictions: List[str]
    confidence: Optional[float] = None
    reasoning: Optional[str] = None

class FanPredictionResponse(BaseModel):
    prediction_id: str
    user_id: str
    race_id: str
    predictions: Dict
    timestamp: datetime
    status: str

class LeaderboardEntry(BaseModel):
    user_id: str
    username: str
    score: float
    correct_predictions: int
    total_predictions: int
    accuracy: float
    rank: int

class LeaderboardResponse(BaseModel):
    race_id: str
    leaderboard: List[LeaderboardEntry]
    total_participants: int
    timestamp: datetime

@router.post("/predictions", response_model=FanPredictionResponse)
async def submit_fan_prediction(prediction: FanPrediction):
    """
    Submit a fan prediction for a race
    
    - **user_id**: Unique user identifier
    - **race_id**: Race identifier
    - **winner_prediction**: Predicted race winner
    - **podium_predictions**: Predicted top 3 finishers
    - **confidence**: Confidence level (0-1)
    - **reasoning**: Optional reasoning for the prediction
    """
    try:
        # Store fan prediction in database
        prediction_id = await store_fan_prediction(prediction)
        
        return FanPredictionResponse(
            prediction_id=prediction_id,
            user_id=prediction.user_id,
            race_id=prediction.race_id,
            predictions={
                "winner": prediction.winner_prediction,
                "podium": prediction.podium_predictions,
                "confidence": prediction.confidence,
                "reasoning": prediction.reasoning
            },
            timestamp=datetime.utcnow(),
            status="submitted"
        )
        
    except Exception as e:
        logger.error(f"Fan prediction submission failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to submit prediction: {str(e)}"
        )

@router.get("/leaderboard/{race_id}", response_model=LeaderboardResponse)
async def get_race_leaderboard(race_id: str, limit: int = 100):
    """
    Get fan prediction leaderboard for a specific race
    
    - **race_id**: Race identifier
    - **limit**: Maximum number of entries to return
    """
    try:
        # Get leaderboard data from database
        leaderboard_data = await get_leaderboard_data(race_id, limit)
        
        return LeaderboardResponse(
            race_id=race_id,
            leaderboard=leaderboard_data['entries'],
            total_participants=leaderboard_data['total'],
            timestamp=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Leaderboard retrieval failed for {race_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get leaderboard: {str(e)}"
        )

@router.get("/predictions/{user_id}")
async def get_user_predictions(user_id: str, race_id: Optional[str] = None):
    """
    Get predictions for a specific user
    
    - **user_id**: User identifier
    - **race_id**: Optional race filter
    """
    try:
        predictions = await get_user_prediction_history(user_id, race_id)
        
        return {
            "user_id": user_id,
            "predictions": predictions,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"User predictions retrieval failed for {user_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get user predictions: {str(e)}"
        )

@router.get("/compare/{user_id}/{race_id}")
async def compare_with_ai(user_id: str, race_id: str):
    """
    Compare user prediction with AI model prediction
    
    - **user_id**: User identifier
    - **race_id**: Race identifier
    """
    try:
        # Get user prediction
        user_prediction = await get_user_prediction(user_id, race_id)
        
        # Get AI prediction
        from app.ml.predictor import RacePredictor
        predictor = RacePredictor()
        ai_prediction = await predictor.get_cached_prediction(race_id)
        
        # Calculate comparison metrics
        comparison = await calculate_prediction_comparison(user_prediction, ai_prediction)
        
        return {
            "user_id": user_id,
            "race_id": race_id,
            "user_prediction": user_prediction,
            "ai_prediction": ai_prediction,
            "comparison": comparison,
            "timestamp": datetime.utcnow()
        }
        
    except Exception as e:
        logger.error(f"Prediction comparison failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to compare predictions: {str(e)}"
        )

# Helper functions (these would be implemented with actual database operations)
async def store_fan_prediction(prediction: FanPrediction) -> str:
    """Store fan prediction in database"""
    # This would implement actual database storage
    import uuid
    return str(uuid.uuid4())

async def get_leaderboard_data(race_id: str, limit: int) -> Dict:
    """Get leaderboard data from database"""
    # Mock data - would be replaced with actual database query
    return {
        "entries": [
            LeaderboardEntry(
                user_id="user1",
                username="F1Fan2024",
                score=95.5,
                correct_predictions=8,
                total_predictions=10,
                accuracy=0.8,
                rank=1
            )
        ],
        "total": 1
    }

async def get_user_prediction_history(user_id: str, race_id: Optional[str] = None) -> List[Dict]:
    """Get user prediction history"""
    # Mock data - would be replaced with actual database query
    return []

async def get_user_prediction(user_id: str, race_id: str) -> Dict:
    """Get specific user prediction"""
    # Mock data - would be replaced with actual database query
    return {}

async def calculate_prediction_comparison(user_pred: Dict, ai_pred: Dict) -> Dict:
    """Calculate comparison metrics between user and AI predictions"""
    # This would implement actual comparison logic
    return {
        "similarity_score": 0.75,
        "differences": [],
        "confidence_comparison": {}
    }
