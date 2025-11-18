"""
Feature engineering module for F1 prediction system
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler, LabelEncoder

from app.core.logging import setup_logging

logger = setup_logging()

class FeatureEngineer:
    """Handles feature engineering for ML models"""
    
    def __init__(self):
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.feature_columns = []
        
    async def create_features(self, race_data: Dict[str, Any]) -> pd.DataFrame:
        """Create comprehensive features for race outcome prediction"""
        try:
            logger.info("Creating features for race prediction")
            
            features = {}
            
            # Driver-based features
            driver_features = self._create_driver_features(race_data.get('driver_data', {}))
            features.update(driver_features)
            
            # Team-based features
            team_features = self._create_team_features(race_data.get('team_data', {}))
            features.update(team_features)
            
            # Track-based features
            track_features = self._create_track_features(race_data.get('race_info', {}))
            features.update(track_features)
            
            # Historical performance features
            historical_features = self._create_historical_features(race_data.get('historical_data', {}))
            features.update(historical_features)
            
            # Season form features
            form_features = self._create_form_features(race_data.get('current_season_data', {}))
            features.update(form_features)
            
            # Session-based features (if available)
            if race_data.get('session_data'):
                session_features = self._create_session_features(race_data['session_data'])
                features.update(session_features)
            
            # Convert to DataFrame
            feature_df = pd.DataFrame([features])
            
            # Handle missing values
            feature_df = self._handle_missing_values(feature_df)
            
            # Scale numerical features
            feature_df = self._scale_features(feature_df)
            
            return feature_df
            
        except Exception as e:
            logger.error(f"Feature creation failed: {e}")
            raise
    
    async def create_podium_features(self, race_data: Dict[str, Any]) -> pd.DataFrame:
        """Create features specifically for podium prediction"""
        try:
            logger.info("Creating podium prediction features")
            
            # Get base features
            base_features = await self.create_features(race_data)
            
            # Add podium-specific features
            podium_features = {}
            
            # Driver podium history
            podium_features.update(self._create_podium_history_features(race_data))
            
            # Team podium performance
            podium_features.update(self._create_team_podium_features(race_data))
            
            # Circuit-specific podium features
            podium_features.update(self._create_circuit_podium_features(race_data))
            
            # Combine with base features
            podium_df = pd.DataFrame([podium_features])
            combined_features = pd.concat([base_features, podium_df], axis=1)
            
            return combined_features
            
        except Exception as e:
            logger.error(f"Podium feature creation failed: {e}")
            raise
    
    async def create_live_features(self, live_data: Dict[str, Any]) -> pd.DataFrame:
        """Create features for live race prediction"""
        try:
            logger.info("Creating live race features")
            
            features = {}
            
            # Current race position features
            features.update(self._create_position_features(live_data))
            
            # Lap time features
            features.update(self._create_lap_time_features(live_data))
            
            # Tire strategy features
            features.update(self._create_tire_features(live_data))
            
            # Gap and interval features
            features.update(self._create_gap_features(live_data))
            
            # Race situation features
            features.update(self._create_race_situation_features(live_data))
            
            # Weather impact features
            features.update(self._create_weather_impact_features(live_data))
            
            # Convert to DataFrame and process
            feature_df = pd.DataFrame([features])
            feature_df = self._handle_missing_values(feature_df)
            feature_df = self._scale_features(feature_df)
            
            return feature_df
            
        except Exception as e:
            logger.error(f"Live feature creation failed: {e}")
            raise
    
    def _create_driver_features(self, driver_data: Dict[str, Any]) -> Dict[str, float]:
        """Create driver-based features"""
        features = {}
        
        drivers = driver_data.get('drivers', [])
        
        for i, driver in enumerate(drivers[:20]):  # Top 20 drivers
            driver_stats = driver.get('statistics', {})
            
            features[f'driver_{i}_wins'] = float(driver_stats.get('wins', 0))
            features[f'driver_{i}_podiums'] = float(driver_stats.get('podiums', 0))
            features[f'driver_{i}_points'] = float(driver_stats.get('points', 0))
            features[f'driver_{i}_avg_finish'] = float(driver_stats.get('avg_finish_position', 10))
            features[f'driver_{i}_dnf_rate'] = float(driver_stats.get('dnf_rate', 0.1))
            features[f'driver_{i}_quali_avg'] = float(driver_stats.get('qualifying_avg', 10))
        
        return features
    
    def _create_team_features(self, team_data: Dict[str, Any]) -> Dict[str, float]:
        """Create team-based features"""
        features = {}
        
        teams = team_data.get('teams', [])
        
        for i, team in enumerate(teams[:10]):  # Top 10 teams
            team_stats = team.get('statistics', {})
            
            features[f'team_{i}_wins'] = float(team_stats.get('wins', 0))
            features[f'team_{i}_podiums'] = float(team_stats.get('podiums', 0))
            features[f'team_{i}_points'] = float(team_stats.get('points', 0))
            features[f'team_{i}_reliability'] = float(team_stats.get('reliability_rate', 0.8))
            features[f'team_{i}_development'] = self._encode_trend(team_stats.get('development_trend', 'stable'))
        
        return features
    
    def _create_track_features(self, race_info: Dict[str, Any]) -> Dict[str, float]:
        """Create track-based features"""
        features = {}
        
        # Circuit characteristics (these would come from a database)
        circuit = race_info.get('circuit', 'unknown')
        
        # Mock track features - would be loaded from database
        track_characteristics = {
            'bahrain': {'length': 5.412, 'turns': 15, 'overtaking': 0.7, 'tire_deg': 0.6},
            'monaco': {'length': 3.337, 'turns': 19, 'overtaking': 0.1, 'tire_deg': 0.3},
            'silverstone': {'length': 5.891, 'turns': 18, 'overtaking': 0.5, 'tire_deg': 0.8}
        }
        
        track_data = track_characteristics.get(circuit, track_characteristics['bahrain'])
        
        features['track_length'] = track_data['length']
        features['track_turns'] = track_data['turns']
        features['overtaking_difficulty'] = track_data['overtaking']
        features['tire_degradation'] = track_data['tire_deg']
        
        return features
    
    def _create_historical_features(self, historical_data: Dict[str, Any]) -> Dict[str, float]:
        """Create historical performance features"""
        features = {}
        
        stats = historical_data.get('statistics', {})
        
        features['pole_advantage'] = float(stats.get('pole_position_advantage', 0.65))
        features['overtaking_freq'] = float(stats.get('overtaking_frequency', 0.25))
        features['safety_car_prob'] = float(stats.get('safety_car_probability', 0.35))
        features['weather_impact'] = self._encode_impact(stats.get('weather_impact', 'medium'))
        
        return features
    
    def _create_form_features(self, season_data: Dict[str, Any]) -> Dict[str, float]:
        """Create current season form features"""
        features = {}
        
        driver_standings = season_data.get('driver_standings', [])
        constructor_standings = season_data.get('constructor_standings', [])
        
        # Driver championship positions
        for i, standing in enumerate(driver_standings[:20]):
            features[f'driver_{i}_championship_pos'] = float(standing.get('position', 20))
            features[f'driver_{i}_championship_points'] = float(standing.get('points', 0))
            features[f'driver_{i}_wins_season'] = float(standing.get('wins', 0))
        
        # Constructor championship positions
        for i, standing in enumerate(constructor_standings[:10]):
            features[f'constructor_{i}_championship_pos'] = float(standing.get('position', 10))
            features[f'constructor_{i}_championship_points'] = float(standing.get('points', 0))
            features[f'constructor_{i}_wins_season'] = float(standing.get('wins', 0))
        
        return features
    
    def _create_session_features(self, session_data: Dict[str, Any]) -> Dict[str, float]:
        """Create practice and qualifying session features"""
        features = {}
        
        # Practice session features
        practice_sessions = session_data.get('practice_sessions', {})
        for session_name, session_info in practice_sessions.items():
            if session_info.get('available'):
                # Would extract lap times, sector times, etc.
                features[f'{session_name}_available'] = 1.0
            else:
                features[f'{session_name}_available'] = 0.0
        
        # Qualifying features
        qualifying = session_data.get('qualifying', {})
        if qualifying.get('available'):
            features['qualifying_available'] = 1.0
            # Would extract qualifying times, positions, etc.
        else:
            features['qualifying_available'] = 0.0
        
        return features
    
    def _create_podium_history_features(self, race_data: Dict[str, Any]) -> Dict[str, float]:
        """Create podium-specific historical features"""
        features = {}
        
        # Driver podium rates at this circuit
        drivers = race_data.get('driver_data', {}).get('drivers', [])
        for i, driver in enumerate(drivers[:20]):
            # This would calculate circuit-specific podium rates
            features[f'driver_{i}_circuit_podium_rate'] = 0.1  # Mock value
        
        return features
    
    def _create_team_podium_features(self, race_data: Dict[str, Any]) -> Dict[str, float]:
        """Create team podium performance features"""
        features = {}
        
        teams = race_data.get('team_data', {}).get('teams', [])
        for i, team in enumerate(teams[:10]):
            # Team podium performance at this circuit
            features[f'team_{i}_circuit_podium_rate'] = 0.2  # Mock value
        
        return features
    
    def _create_circuit_podium_features(self, race_data: Dict[str, Any]) -> Dict[str, float]:
        """Create circuit-specific podium features"""
        features = {}
        
        # Circuit characteristics affecting podium chances
        features['circuit_podium_consistency'] = 0.7  # How consistent podium finishers are
        features['circuit_surprise_factor'] = 0.3     # How often unexpected podiums occur
        
        return features
    
    def _create_position_features(self, live_data: Dict[str, Any]) -> Dict[str, float]:
        """Create current position-based features"""
        features = {}
        
        positions = live_data.get('positions', [])
        for i, pos_data in enumerate(positions[:20]):
            features[f'current_position_{i}'] = float(pos_data.get('position', 20))
            features[f'grid_position_{i}'] = float(pos_data.get('grid_position', 20))
            features[f'positions_gained_{i}'] = float(pos_data.get('positions_gained', 0))
        
        return features
    
    def _create_lap_time_features(self, live_data: Dict[str, Any]) -> Dict[str, float]:
        """Create lap time-based features"""
        features = {}
        
        lap_times = live_data.get('lap_times', {})
        for driver_id, times in lap_times.items():
            if isinstance(times, list) and times:
                features[f'avg_lap_time_{driver_id}'] = float(np.mean(times))
                features[f'lap_time_consistency_{driver_id}'] = float(np.std(times))
                features[f'recent_pace_{driver_id}'] = float(np.mean(times[-3:]) if len(times) >= 3 else np.mean(times))
        
        return features
    
    def _create_tire_features(self, live_data: Dict[str, Any]) -> Dict[str, float]:
        """Create tire strategy features"""
        features = {}
        
        tire_data = live_data.get('tire_data', {})
        for driver_id, tire_info in tire_data.items():
            features[f'tire_age_{driver_id}'] = float(tire_info.get('age', 0))
            features[f'tire_compound_{driver_id}'] = self._encode_tire_compound(tire_info.get('compound', 'medium'))
            features[f'pit_stops_{driver_id}'] = float(tire_info.get('pit_stops', 0))
        
        return features
    
    def _create_gap_features(self, live_data: Dict[str, Any]) -> Dict[str, float]:
        """Create gap and interval features"""
        features = {}
        
        # Gap to leader, gap to car ahead, etc.
        positions = live_data.get('positions', [])
        for i, pos_data in enumerate(positions[:20]):
            features[f'gap_to_leader_{i}'] = float(pos_data.get('gap_to_leader', 999))
            features[f'gap_to_ahead_{i}'] = float(pos_data.get('gap_to_ahead', 999))
            features[f'gap_to_behind_{i}'] = float(pos_data.get('gap_to_behind', 999))
        
        return features
    
    def _create_race_situation_features(self, live_data: Dict[str, Any]) -> Dict[str, float]:
        """Create race situation features"""
        features = {}
        
        features['current_lap'] = float(live_data.get('current_lap', 1))
        features['total_laps'] = float(live_data.get('total_laps', 58))
        features['race_progress'] = float(live_data.get('current_lap', 1)) / float(live_data.get('total_laps', 58))
        features['safety_car_active'] = 1.0 if live_data.get('safety_car', False) else 0.0
        
        return features
    
    def _create_weather_impact_features(self, live_data: Dict[str, Any]) -> Dict[str, float]:
        """Create weather impact features"""
        features = {}
        
        weather = live_data.get('weather', {})
        features['temperature'] = float(weather.get('temperature', 25))
        features['humidity'] = float(weather.get('humidity', 50))
        features['wind_speed'] = float(weather.get('wind_speed', 5))
        features['precipitation'] = 1.0 if weather.get('precipitation', False) else 0.0
        
        return features
    
    def _handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle missing values in features"""
        # Fill numerical columns with median
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        df[numerical_cols] = df[numerical_cols].fillna(df[numerical_cols].median())
        
        # Fill categorical columns with mode
        categorical_cols = df.select_dtypes(include=['object']).columns
        for col in categorical_cols:
            df[col] = df[col].fillna(df[col].mode()[0] if not df[col].mode().empty else 'unknown')
        
        return df
    
    def _scale_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """Scale numerical features"""
        numerical_cols = df.select_dtypes(include=[np.number]).columns
        df[numerical_cols] = self.scaler.fit_transform(df[numerical_cols])
        return df
    
    def _encode_trend(self, trend: str) -> float:
        """Encode development trend"""
        trend_mapping = {'improving': 1.0, 'stable': 0.0, 'declining': -1.0}
        return trend_mapping.get(trend, 0.0)
    
    def _encode_impact(self, impact: str) -> float:
        """Encode impact level"""
        impact_mapping = {'low': 0.2, 'medium': 0.5, 'high': 0.8}
        return impact_mapping.get(impact, 0.5)
    
    def _encode_tire_compound(self, compound: str) -> float:
        """Encode tire compound"""
        compound_mapping = {'soft': 1.0, 'medium': 0.5, 'hard': 0.0, 'intermediate': 0.3, 'wet': 0.7}
        return compound_mapping.get(compound, 0.5)
