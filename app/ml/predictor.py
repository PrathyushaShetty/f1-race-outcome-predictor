"""
F1 Race Outcome Predictor - Main ML Engine
"""

import asyncio
import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import joblib
import os

from app.core.config import settings
from app.core.logging import setup_logging
from app.ml.data_processor import DataProcessor
from app.ml.feature_engineer import FeatureEngineer
from app.ml.models import EnsembleModel

logger = setup_logging()

class RacePredictor:
    """Main race prediction engine"""
    
    def __init__(self):
        self.data_processor = DataProcessor()
        self.feature_engineer = FeatureEngineer()
        self.ensemble_model = EnsembleModel()
        self.models_loaded = False
        
    async def load_race_data(self, race_id: str) -> Dict[str, Any]:
        """Load and prepare race data for prediction"""
        try:
            logger.info(f"Loading race data for {race_id}")
            
            # Parse race ID to get year and race info
            race_info = self._parse_race_id(race_id)
            
            # Load historical data
            historical_data = await self.data_processor.load_historical_data(
                race_info['circuit'], race_info['year']
            )
            
            # Load current season data
            current_season_data = await self.data_processor.load_current_season_data(
                race_info['year']
            )
            
            # Load driver and team data
            driver_data = await self.data_processor.load_driver_data(race_info['year'])
            team_data = await self.data_processor.load_team_data(race_info['year'])
            
            # Load practice and qualifying data (if available)
            session_data = await self.data_processor.load_session_data(race_id)
            
            return {
                'race_info': race_info,
                'historical_data': historical_data,
                'current_season_data': current_season_data,
                'driver_data': driver_data,
                'team_data': team_data,
                'session_data': session_data
            }
            
        except Exception as e:
            logger.error(f"Failed to load race data for {race_id}: {e}")
            raise
    
    async def predict_race_outcome(self, race_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive race outcome predictions"""
        try:
            logger.info("Generating race outcome predictions")
            
            # Engineer features
            features = await self.feature_engineer.create_features(race_data)
            
            # Load models if not already loaded
            if not self.models_loaded:
                await self.ensemble_model.load_models()
                self.models_loaded = True
            
            # Generate predictions
            predictions = await self.ensemble_model.predict(features)
            
            # Post-process predictions
            processed_predictions = self._process_predictions(predictions, race_data)
            
            return processed_predictions
            
        except Exception as e:
            logger.error(f"Race prediction failed: {e}")
            raise
    
    async def predict_podium_probabilities(self, race_id: str) -> List[Dict[str, Any]]:
        """Generate podium finish probabilities for all drivers"""
        try:
            logger.info(f"Generating podium probabilities for {race_id}")
            
            # Load race data
            race_data = await self.load_race_data(race_id)
            
            # Engineer features for podium prediction
            features = await self.feature_engineer.create_podium_features(race_data)
            
            # Generate podium probabilities
            podium_probs = await self.ensemble_model.predict_podium(features)
            
            # Format results
            drivers = race_data['driver_data']['drivers']
            results = []
            
            for i, driver in enumerate(drivers):
                results.append({
                    'driver': driver['name'],
                    'driver_code': driver['code'],
                    'team': driver['team'],
                    'podium_probability': float(podium_probs[i]),
                    'win_probability': float(podium_probs[i] * 0.33),  # Simplified calculation
                })
            
            # Sort by probability
            results.sort(key=lambda x: x['podium_probability'], reverse=True)
            
            return results
            
        except Exception as e:
            logger.error(f"Podium prediction failed: {e}")
            raise
    
    async def get_live_race_data(self, race_id: str, lap: Optional[int] = None) -> Dict[str, Any]:
        """Get live race data for real-time predictions"""
        try:
            logger.info(f"Getting live race data for {race_id}, lap {lap}")
            
            # This would connect to live F1 timing data
            # For now, return mock data structure
            return {
                'race_id': race_id,
                'current_lap': lap or 1,
                'total_laps': 58,
                'positions': [],
                'lap_times': {},
                'tire_data': {},
                'weather': {},
                'safety_car': False,
                'timestamp': datetime.utcnow()
            }
            
        except Exception as e:
            logger.error(f"Failed to get live race data: {e}")
            raise
    
    async def predict_live_race_outcome(self, live_data: Dict[str, Any]) -> Dict[str, Any]:
        """Generate live race predictions during ongoing race"""
        try:
            logger.info("Generating live race predictions")
            
            # Engineer live features
            live_features = await self.feature_engineer.create_live_features(live_data)
            
            # Generate live predictions
            live_predictions = await self.ensemble_model.predict_live(live_features)
            
            return {
                'probabilities': live_predictions.get('win_probabilities', {}),
                'position_changes': live_predictions.get('position_changes', []),
                'pit_strategy_recommendations': live_predictions.get('pit_strategies', {}),
                'race_pace_analysis': live_predictions.get('pace_analysis', {}),
                'confidence': live_predictions.get('confidence', 0.0)
            }
            
        except Exception as e:
            logger.error(f"Live prediction failed: {e}")
            raise
    
    async def get_weather_forecast(self, race_id: str) -> Dict[str, Any]:
        """Get weather forecast for race location"""
        try:
            # This would integrate with weather APIs
            # For now, return mock data
            return {
                'temperature': 25.0,
                'humidity': 65,
                'wind_speed': 10.5,
                'precipitation_chance': 20,
                'conditions': 'partly_cloudy',
                'forecast_confidence': 0.85
            }
            
        except Exception as e:
            logger.error(f"Weather forecast failed: {e}")
            return {}
    
    async def get_track_characteristics(self, race_id: str) -> Dict[str, Any]:
        """Get track characteristics and historical performance data"""
        try:
            race_info = self._parse_race_id(race_id)
            circuit = race_info['circuit']
            
            # This would load from track database
            # For now, return mock data
            return {
                'circuit_name': circuit,
                'length': 5.412,  # km
                'turns': 19,
                'drs_zones': 2,
                'overtaking_difficulty': 'medium',
                'tire_degradation': 'high',
                'historical_pole_advantage': 0.65,
                'safety_car_probability': 0.35
            }
            
        except Exception as e:
            logger.error(f"Track characteristics failed: {e}")
            return {}
    
    async def get_cached_prediction(self, race_id: str) -> Dict[str, Any]:
        """Get cached prediction for comparison with fan predictions"""
        try:
            # This would implement caching logic
            # For now, generate fresh prediction
            race_data = await self.load_race_data(race_id)
            return await self.predict_race_outcome(race_data)
            
        except Exception as e:
            logger.error(f"Cached prediction retrieval failed: {e}")
            raise
    
    def _parse_race_id(self, race_id: str) -> Dict[str, str]:
        """Parse race ID to extract race information"""
        # Example: 'bahrain-2024' -> {'circuit': 'bahrain', 'year': '2024'}
        parts = race_id.split('-')
        if len(parts) >= 2:
            return {
                'circuit': parts[0],
                'year': parts[1],
                'race_id': race_id
            }
        else:
            return {
                'circuit': race_id,
                'year': '2024',
                'race_id': race_id
            }
    
    def _process_predictions(self, predictions: Dict[str, Any], race_data: Dict[str, Any]) -> Dict[str, Any]:
        """Post-process raw model predictions"""
        try:
            # Extract and format predictions
            processed = {
                'winner': predictions.get('predicted_winner', 'Unknown'),
                'top_10': predictions.get('top_10_order', []),
                'confidence': float(predictions.get('confidence', 0.0)),
                'win_probabilities': predictions.get('win_probabilities', {}),
                'team_performance': predictions.get('team_predictions', {}),
                'strategic_insights': self._generate_strategic_insights(predictions, race_data)
            }
            
            return processed
            
        except Exception as e:
            logger.error(f"Prediction processing failed: {e}")
            return {'error': str(e)}
    
    def _generate_strategic_insights(self, predictions: Dict[str, Any], race_data: Dict[str, Any]) -> List[str]:
        """Generate strategic insights from predictions"""
        insights = []
        
        # Add weather-based insights
        if 'weather' in race_data:
            insights.append("Weather conditions favor aerodynamically efficient cars")
        
        # Add track-specific insights
        insights.append("Track characteristics suggest tire strategy will be crucial")
        
        # Add form-based insights
        insights.append("Recent form indicates strong performance from top teams")
        
        return insights
