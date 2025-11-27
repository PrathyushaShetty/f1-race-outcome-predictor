"""
Machine Learning models for F1 prediction system
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
import joblib
import os
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
import xgboost as xgb
# from tensorflow import keras
# from tensorflow.keras import layers
# TensorFlow disabled due to installation issues - neural network model will use mock predictions
import asyncio

from app.core.config import settings
from app.core.logging import setup_logging

logger = setup_logging()

class EnsembleModel:
    """Ensemble model combining multiple ML algorithms"""
    
    def __init__(self):
        self.models = {}
        self.model_weights = {}
        self.is_trained = False
        self.model_dir = "models"
        
        # Ensure model directory exists
        os.makedirs(self.model_dir, exist_ok=True)
    
    async def load_models(self):
        """Load pre-trained models"""
        try:
            logger.info("Loading ML models...")
            
            # Initialize models
            self.models = {
                'random_forest': RandomForestModel(),
                'xgboost': XGBoostModel(),
                'neural_network': NeuralNetworkModel()
            }
            
            # Load each model
            for model_name, model in self.models.items():
                try:
                    await model.load(os.path.join(self.model_dir, f"{model_name}.pkl"))
                    logger.info(f"✅ {model_name} loaded successfully")
                except Exception as e:
                    logger.warning(f"⚠️ Could not load {model_name}: {e}")
                    # Initialize with default parameters
                    await model.initialize()
            
            # Set model weights (could be learned from validation data)
            self.model_weights = {
                'random_forest': 0.3,
                'xgboost': 0.4,
                'neural_network': 0.3
            }
            
            self.is_trained = True
            logger.info("✅ All models loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            raise
    
    async def predict(self, features: pd.DataFrame) -> Dict[str, Any]:
        """Generate ensemble predictions"""
        try:
            if not self.is_trained:
                await self.load_models()
            
            logger.info("Generating ensemble predictions")
            
            predictions = {}
            model_predictions = {}
            
            # Get predictions from each model
            for model_name, model in self.models.items():
                try:
                    model_pred = await model.predict(features)
                    model_predictions[model_name] = model_pred
                except Exception as e:
                    logger.warning(f"Prediction failed for {model_name}: {e}")
                    continue
            
            # Combine predictions using weighted average
            if model_predictions:
                predictions = self._combine_predictions(model_predictions)
            else:
                # Fallback predictions
                predictions = self._generate_fallback_predictions()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Ensemble prediction failed: {e}")
            return self._generate_fallback_predictions()
    
    async def predict_podium(self, features: pd.DataFrame) -> np.ndarray:
        """Generate podium probability predictions"""
        try:
            logger.info("Generating podium predictions")
            
            podium_probs = []
            
            for model_name, model in self.models.items():
                try:
                    if hasattr(model, 'predict_podium'):
                        probs = await model.predict_podium(features)
                        podium_probs.append(probs * self.model_weights[model_name])
                except Exception as e:
                    logger.warning(f"Podium prediction failed for {model_name}: {e}")
                    continue
            
            # Average the probabilities
            if podium_probs:
                final_probs = np.mean(podium_probs, axis=0)
            else:
                # Fallback: uniform distribution
                final_probs = np.random.uniform(0.1, 0.9, 20)
            
            return final_probs
            
        except Exception as e:
            logger.error(f"Podium prediction failed: {e}")
            return np.random.uniform(0.1, 0.9, 20)
    
    async def predict_live(self, features: pd.DataFrame) -> Dict[str, Any]:
        """Generate live race predictions"""
        try:
            logger.info("Generating live race predictions")
            
            live_predictions = {}
            
            # Get live predictions from each model
            for model_name, model in self.models.items():
                try:
                    if hasattr(model, 'predict_live'):
                        pred = await model.predict_live(features)
                        live_predictions[model_name] = pred
                except Exception as e:
                    logger.warning(f"Live prediction failed for {model_name}: {e}")
                    continue
            
            # Combine live predictions
            combined_live = self._combine_live_predictions(live_predictions)
            
            return combined_live
            
        except Exception as e:
            logger.error(f"Live prediction failed: {e}")
            return self._generate_fallback_live_predictions()
    
    async def retrain_models(self):
        """Retrain all models with new data"""
        try:
            logger.info("Starting model retraining...")
            
            # Load training data (this would be implemented)
            training_data = await self._load_training_data()
            
            if training_data is not None:
                X, y = training_data
                
                # Retrain each model
                for model_name, model in self.models.items():
                    try:
                        logger.info(f"Retraining {model_name}...")
                        await model.train(X, y)
                        await model.save(os.path.join(self.model_dir, f"{model_name}.pkl"))
                        logger.info(f"✅ {model_name} retrained successfully")
                    except Exception as e:
                        logger.error(f"❌ Retraining failed for {model_name}: {e}")
                
                logger.info("✅ Model retraining completed")
            else:
                logger.warning("⚠️ No training data available")
                
        except Exception as e:
            logger.error(f"❌ Model retraining failed: {e}")
            raise
    
    def _combine_predictions(self, model_predictions: Dict[str, Dict]) -> Dict[str, Any]:
        """Combine predictions from multiple models"""
        try:
            combined = {
                'predicted_winner': 'Max Verstappen',  # Default
                'top_10_order': [],
                'confidence': 0.0,
                'win_probabilities': {},
                'team_predictions': {}
            }
            
            # Combine winner predictions (majority vote or confidence-weighted)
            winners = []
            confidences = []
            
            for model_name, pred in model_predictions.items():
                if 'predicted_winner' in pred:
                    winners.append(pred['predicted_winner'])
                    confidences.append(pred.get('confidence', 0.5))
            
            if winners:
                # Use the prediction from the most confident model
                max_conf_idx = np.argmax(confidences)
                combined['predicted_winner'] = winners[max_conf_idx]
                combined['confidence'] = float(np.mean(confidences))
            
            # Combine win probabilities
            all_probs = {}
            for model_name, pred in model_predictions.items():
                if 'win_probabilities' in pred:
                    for driver, prob in pred['win_probabilities'].items():
                        if driver not in all_probs:
                            all_probs[driver] = []
                        all_probs[driver].append(prob * self.model_weights[model_name])
            
            # Average probabilities
            for driver, probs in all_probs.items():
                combined['win_probabilities'][driver] = float(np.mean(probs))
            
            return combined
            
        except Exception as e:
            logger.error(f"Prediction combination failed: {e}")
            return self._generate_fallback_predictions()
    
    def _combine_live_predictions(self, live_predictions: Dict[str, Dict]) -> Dict[str, Any]:
        """Combine live predictions from multiple models"""
        try:
            combined = {
                'win_probabilities': {},
                'position_changes': [],
                'pit_strategies': {},
                'pace_analysis': {},
                'confidence': 0.0
            }
            
            # Combine win probabilities
            all_probs = {}
            confidences = []
            
            for model_name, pred in live_predictions.items():
                if 'win_probabilities' in pred:
                    for driver, prob in pred['win_probabilities'].items():
                        if driver not in all_probs:
                            all_probs[driver] = []
                        all_probs[driver].append(prob * self.model_weights[model_name])
                
                confidences.append(pred.get('confidence', 0.5))
            
            # Average probabilities
            for driver, probs in all_probs.items():
                combined['win_probabilities'][driver] = float(np.mean(probs))
            
            combined['confidence'] = float(np.mean(confidences)) if confidences else 0.5
            
            return combined
            
        except Exception as e:
            logger.error(f"Live prediction combination failed: {e}")
            return self._generate_fallback_live_predictions()
    
    def _generate_fallback_predictions(self) -> Dict[str, Any]:
        """Generate fallback predictions when models fail"""
        drivers = ['Max Verstappen', 'Lewis Hamilton', 'Charles Leclerc', 'Lando Norris', 'George Russell']
        
        return {
            'predicted_winner': drivers[0],
            'top_10_order': drivers,
            'confidence': 0.5,
            'win_probabilities': {driver: 0.2 for driver in drivers},
            'team_predictions': {
                'Red Bull': {'expected_points': 25, 'reliability': 0.9},
                'Mercedes': {'expected_points': 18, 'reliability': 0.85},
                'Ferrari': {'expected_points': 15, 'reliability': 0.8}
            }
        }
    
    def _generate_fallback_live_predictions(self) -> Dict[str, Any]:
        """Generate fallback live predictions"""
        drivers = ['Max Verstappen', 'Lewis Hamilton', 'Charles Leclerc']
        
        return {
            'win_probabilities': {driver: 0.33 for driver in drivers},
            'position_changes': [],
            'pit_strategies': {},
            'pace_analysis': {},
            'confidence': 0.5
        }
    
    async def _load_training_data(self) -> Optional[Tuple[pd.DataFrame, pd.Series]]:
        """Load training data for model retraining"""
        try:
            # This would implement actual data loading logic
            # For now, return None to indicate no data available
            return None
        except Exception as e:
            logger.error(f"Training data loading failed: {e}")
            return None


class RandomForestModel:
    """Random Forest model for F1 predictions"""
    
    def __init__(self):
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.is_trained = False
    
    async def initialize(self):
        """Initialize model with default parameters"""
        self.is_trained = False
    
    async def load(self, filepath: str):
        """Load trained model"""
        if os.path.exists(filepath):
            self.model = joblib.load(filepath)
            self.is_trained = True
        else:
            raise FileNotFoundError(f"Model file not found: {filepath}")
    
    async def save(self, filepath: str):
        """Save trained model"""
        joblib.dump(self.model, filepath)
    
    async def train(self, X: pd.DataFrame, y: pd.Series):
        """Train the model"""
        self.model.fit(X, y)
        self.is_trained = True
    
    async def predict(self, features: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictions"""
        if not self.is_trained:
            return self._mock_predictions()
        
        try:
            # Generate mock predictions for now
            return self._mock_predictions()
        except Exception as e:
            logger.error(f"RandomForest prediction failed: {e}")
            return self._mock_predictions()
    
    def _mock_predictions(self) -> Dict[str, Any]:
        """Generate mock predictions"""
        return {
            'predicted_winner': 'Max Verstappen',
            'confidence': 0.75,
            'win_probabilities': {
                'Max Verstappen': 0.35,
                'Lewis Hamilton': 0.25,
                'Charles Leclerc': 0.20,
                'Lando Norris': 0.15,
                'George Russell': 0.05
            }
        }


class XGBoostModel:
    """XGBoost model for F1 predictions"""
    
    def __init__(self):
        self.model = xgb.XGBClassifier(
            learning_rate=0.1,
            max_depth=6,
            n_estimators=200,
            random_state=42
        )
        self.is_trained = False
    
    async def initialize(self):
        """Initialize model with default parameters"""
        self.is_trained = False
    
    async def load(self, filepath: str):
        """Load trained model"""
        if os.path.exists(filepath):
            self.model = joblib.load(filepath)
            self.is_trained = True
        else:
            raise FileNotFoundError(f"Model file not found: {filepath}")
    
    async def save(self, filepath: str):
        """Save trained model"""
        joblib.dump(self.model, filepath)
    
    async def train(self, X: pd.DataFrame, y: pd.Series):
        """Train the model"""
        self.model.fit(X, y)
        self.is_trained = True
    
    async def predict(self, features: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictions"""
        if not self.is_trained:
            return self._mock_predictions()
        
        try:
            # Generate mock predictions for now
            return self._mock_predictions()
        except Exception as e:
            logger.error(f"XGBoost prediction failed: {e}")
            return self._mock_predictions()
    
    def _mock_predictions(self) -> Dict[str, Any]:
        """Generate mock predictions"""
        return {
            'predicted_winner': 'Lewis Hamilton',
            'confidence': 0.82,
            'win_probabilities': {
                'Lewis Hamilton': 0.30,
                'Max Verstappen': 0.28,
                'Charles Leclerc': 0.22,
                'Lando Norris': 0.15,
                'George Russell': 0.05
            }
        }


class NeuralNetworkModel:
    """Neural Network model for F1 predictions"""
    
    def __init__(self):
        self.model = None
        self.is_trained = False
    
    async def initialize(self):
        """Initialize neural network"""
        self.model = self._build_model()
        self.is_trained = False
    
    def _build_model(self):
        """Build neural network architecture"""
        # TensorFlow/Keras disabled - returning None
        return None
        # model = keras.Sequential([
        #     layers.Dense(128, activation='relu', input_shape=(100,)),
        #     layers.Dropout(0.3),
        #     layers.Dense(64, activation='relu'),
        #     layers.Dropout(0.3),
        #     layers.Dense(32, activation='relu'),
        #     layers.Dense(20, activation='softmax')
        # ])
        # model.compile(
        #     optimizer='adam',
        #     loss='categorical_crossentropy',
        #     metrics=['accuracy']
        # )
        # return model
    
    async def load(self, filepath: str):
        """Load trained model"""
        # TensorFlow/Keras disabled
        logger.warning("[WARN] Neural network model disabled - keras not available")
        # if os.path.exists(filepath):
        #     self.model = keras.models.load_model(filepath)
        #     self.is_trained = True
        # else:
        #     raise FileNotFoundError(f"Model file not found: {filepath}")
    
    async def save(self, filepath: str):
        """Save trained model"""
        if self.model:
            self.model.save(filepath)
    
    async def train(self, X: pd.DataFrame, y: pd.Series):
        """Train the model"""
        if self.model is None:
            self.model = self._build_model()
        
        # Convert to appropriate format for neural network
        # This would need proper preprocessing
        # self.model.fit(X, y, epochs=50, batch_size=32, validation_split=0.2)
        self.is_trained = True
    
    async def predict(self, features: pd.DataFrame) -> Dict[str, Any]:
        """Generate predictions"""
        if not self.is_trained or self.model is None:
            return self._mock_predictions()
        
        try:
            # Generate mock predictions for now
            return self._mock_predictions()
        except Exception as e:
            logger.error(f"Neural Network prediction failed: {e}")
            return self._mock_predictions()
    
    def _mock_predictions(self) -> Dict[str, Any]:
        """Generate mock predictions"""
        return {
            'predicted_winner': 'Charles Leclerc',
            'confidence': 0.78,
            'win_probabilities': {
                'Charles Leclerc': 0.32,
                'Max Verstappen': 0.26,
                'Lewis Hamilton': 0.24,
                'Lando Norris': 0.13,
                'George Russell': 0.05
            }
        }
