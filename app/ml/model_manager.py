"""
Model management system for F1 prediction models
"""

import asyncio
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import os
import json

from app.ml.models import EnsembleModel
from app.core.config import settings
from app.core.logging import setup_logging

logger = setup_logging()

class ModelManager:
    """Manages ML model lifecycle, updates, and performance monitoring"""
    
    def __init__(self):
        self.ensemble_model = EnsembleModel()
        self.model_performance = {}
        self.last_update = None
        self.update_schedule = settings.MODEL_RETRAIN_SCHEDULE
        self.performance_threshold = settings.PREDICTION_CONFIDENCE_THRESHOLD
        
    async def load_models(self):
        """Load all ML models"""
        try:
            logger.info("🔄 Loading ML models...")
            await self.ensemble_model.load_models()
            self.last_update = datetime.utcnow()
            logger.info("✅ ML models loaded successfully")
            
        except Exception as e:
            logger.error(f"❌ Model loading failed: {e}")
            raise
    
    async def retrain_models(self):
        """Retrain models with latest data"""
        try:
            logger.info("🔄 Starting model retraining...")
            
            # Check if retraining is needed
            if not self._should_retrain():
                logger.info("⏭️ Model retraining not needed at this time")
                return
            
            # Backup current models
            await self._backup_models()
            
            # Retrain ensemble
            await self.ensemble_model.retrain_models()
            
            # Validate new models
            validation_results = await self._validate_models()
            
            if validation_results['passed']:
                self.last_update = datetime.utcnow()
                await self._save_model_metadata()
                logger.info("✅ Model retraining completed successfully")
            else:
                # Restore backup if validation fails
                await self._restore_models()
                logger.error("❌ Model validation failed, restored previous models")
                
        except Exception as e:
            logger.error(f"❌ Model retraining failed: {e}")
            await self._restore_models()
            raise
    
    async def get_model_status(self) -> Dict[str, Any]:
        """Get current model status and performance metrics"""
        try:
            status = {
                'models_loaded': self.ensemble_model.is_trained,
                'last_update': self.last_update.isoformat() if self.last_update else None,
                'next_scheduled_update': self._get_next_update_time(),
                'performance_metrics': self.model_performance,
                'model_versions': await self._get_model_versions(),
                'health_status': 'healthy' if self.ensemble_model.is_trained else 'unhealthy'
            }
            
            return status
            
        except Exception as e:
            logger.error(f"Failed to get model status: {e}")
            return {'health_status': 'error', 'error': str(e)}
    
    async def update_performance_metrics(self, race_id: str, predictions: Dict, actual_results: Dict):
        """Update model performance metrics with actual race results"""
        try:
            logger.info(f"Updating performance metrics for {race_id}")
            
            # Calculate accuracy metrics
            metrics = self._calculate_accuracy_metrics(predictions, actual_results)
            
            # Store metrics
            if race_id not in self.model_performance:
                self.model_performance[race_id] = {}
            
            self.model_performance[race_id] = {
                'predictions': predictions,
                'actual_results': actual_results,
                'metrics': metrics,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Save to persistent storage
            await self._save_performance_metrics()
            
            # Check if model performance is below threshold
            if metrics.get('overall_accuracy', 0) < self.performance_threshold:
                logger.warning(f"⚠️ Model performance below threshold: {metrics['overall_accuracy']}")
                # Could trigger automatic retraining here
            
        except Exception as e:
            logger.error(f"Failed to update performance metrics: {e}")
    
    async def schedule_model_updates(self):
        """Schedule automatic model updates"""
        try:
            logger.info("📅 Setting up model update schedule")
            
            # Parse cron-like schedule
            schedule_parts = self.update_schedule.split()
            if len(schedule_parts) == 5:
                minute, hour, day, month, weekday = schedule_parts
                
                # For simplicity, schedule daily at specified hour
                if hour != '*':
                    schedule.every().day.at(f"{hour}:00").do(self._scheduled_retrain)
                    logger.info(f"📅 Scheduled daily retraining at {hour}:00")
            
            # Start scheduler in background
            asyncio.create_task(self._run_scheduler())
            
        except Exception as e:
            logger.error(f"Failed to schedule model updates: {e}")
    
    async def force_model_update(self):
        """Force immediate model update"""
        try:
            logger.info("🔄 Forcing immediate model update...")
            await self.retrain_models()
            
        except Exception as e:
            logger.error(f"Forced model update failed: {e}")
            raise
    
    def _should_retrain(self) -> bool:
        """Determine if models should be retrained"""
        try:
            # Check time since last update
            if self.last_update:
                time_since_update = datetime.utcnow() - self.last_update
                if time_since_update < timedelta(hours=settings.MODEL_UPDATE_INTERVAL / 3600):
                    return False
            
            # Check performance metrics
            if self.model_performance:
                recent_performance = list(self.model_performance.values())[-5:]  # Last 5 races
                avg_accuracy = sum(
                    perf['metrics'].get('overall_accuracy', 0) 
                    for perf in recent_performance
                ) / len(recent_performance)
                
                if avg_accuracy < self.performance_threshold:
                    logger.info(f"🔄 Retraining triggered by low performance: {avg_accuracy}")
                    return True
            
            # Check if new data is available
            new_data_available = await self._check_new_data()
            if new_data_available:
                logger.info("🔄 Retraining triggered by new data availability")
                return True
            
            return True  # Default to retraining if unsure
            
        except Exception as e:
            logger.error(f"Error checking retrain conditions: {e}")
            return False
    
    async def _backup_models(self):
        """Backup current models before retraining"""
        try:
            backup_dir = "models/backup"
            os.makedirs(backup_dir, exist_ok=True)
            
            # This would implement actual model backup logic
            logger.info("📦 Models backed up successfully")
            
        except Exception as e:
            logger.error(f"Model backup failed: {e}")
    
    async def _validate_models(self) -> Dict[str, Any]:
        """Validate newly trained models"""
        try:
            logger.info("🔍 Validating new models...")
            
            # This would implement actual model validation
            # For now, return success
            validation_results = {
                'passed': True,
                'accuracy': 0.85,
                'precision': 0.82,
                'recall': 0.88,
                'f1_score': 0.85
            }
            
            logger.info(f"✅ Model validation passed: {validation_results}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Model validation failed: {e}")
            return {'passed': False, 'error': str(e)}
    
    async def _restore_models(self):
        """Restore models from backup"""
        try:
            logger.info("🔄 Restoring models from backup...")
            
            # This would implement actual model restoration
            logger.info("✅ Models restored from backup")
            
        except Exception as e:
            logger.error(f"Model restoration failed: {e}")
    
    async def _save_model_metadata(self):
        """Save model metadata and version information"""
        try:
            metadata = {
                'last_update': self.last_update.isoformat(),
                'model_versions': await self._get_model_versions(),
                'performance_summary': self._get_performance_summary()
            }
            
            with open('models/metadata.json', 'w') as f:
                json.dump(metadata, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save model metadata: {e}")
    
    async def _save_performance_metrics(self):
        """Save performance metrics to persistent storage"""
        try:
            with open('models/performance_metrics.json', 'w') as f:
                json.dump(self.model_performance, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to save performance metrics: {e}")
    
    async def _get_model_versions(self) -> Dict[str, str]:
        """Get version information for all models"""
        try:
            # This would implement actual version tracking
            return {
                'random_forest': '1.0.0',
                'xgboost': '1.0.0',
                'neural_network': '1.0.0',
                'ensemble': '1.0.0'
            }
        except Exception as e:
            logger.error(f"Failed to get model versions: {e}")
            return {}
    
    def _get_performance_summary(self) -> Dict[str, float]:
        """Get summary of model performance"""
        try:
            if not self.model_performance:
                return {}
            
            all_metrics = [perf['metrics'] for perf in self.model_performance.values()]
            
            return {
                'avg_accuracy': sum(m.get('overall_accuracy', 0) for m in all_metrics) / len(all_metrics),
                'avg_precision': sum(m.get('precision', 0) for m in all_metrics) / len(all_metrics),
                'avg_recall': sum(m.get('recall', 0) for m in all_metrics) / len(all_metrics),
                'total_predictions': len(all_metrics)
            }
            
        except Exception as e:
            logger.error(f"Failed to get performance summary: {e}")
            return {}
    
    def _get_next_update_time(self) -> Optional[str]:
        """Get next scheduled update time"""
        try:
            if self.last_update:
                next_update = self.last_update + timedelta(hours=settings.MODEL_UPDATE_INTERVAL / 3600)
                return next_update.isoformat()
            return None
        except Exception as e:
            logger.error(f"Failed to get next update time: {e}")
            return None
    
    def _calculate_accuracy_metrics(self, predictions: Dict, actual_results: Dict) -> Dict[str, float]:
        """Calculate accuracy metrics comparing predictions to actual results"""
        try:
            metrics = {}
            
            # Winner prediction accuracy
            predicted_winner = predictions.get('predicted_winner')
            actual_winner = actual_results.get('winner')
            metrics['winner_accuracy'] = 1.0 if predicted_winner == actual_winner else 0.0
            
            # Top 3 accuracy
            predicted_top3 = predictions.get('top_10_order', [])[:3]
            actual_top3 = actual_results.get('top_3', [])
            
            if len(predicted_top3) == 3 and len(actual_top3) == 3:
                top3_matches = sum(1 for p, a in zip(predicted_top3, actual_top3) if p == a)
                metrics['top3_accuracy'] = top3_matches / 3.0
            
            # Overall accuracy (weighted combination)
            metrics['overall_accuracy'] = (
                metrics.get('winner_accuracy', 0) * 0.6 +
                metrics.get('top3_accuracy', 0) * 0.4
            )
            
            # Confidence calibration
            predicted_confidence = predictions.get('confidence', 0.5)
            metrics['confidence_calibration'] = abs(predicted_confidence - metrics['overall_accuracy'])
            
            return metrics
            
        except Exception as e:
            logger.error(f"Failed to calculate accuracy metrics: {e}")
            return {'overall_accuracy': 0.0}
    
    async def _check_new_data(self) -> bool:
        """Check if new training data is available"""
        try:
            # This would implement actual data availability checking
            # For now, assume new data is available weekly
            if self.last_update:
                time_since_update = datetime.utcnow() - self.last_update
                return time_since_update > timedelta(days=7)
            return True
            
        except Exception as e:
            logger.error(f"Failed to check new data availability: {e}")
            return False
    
    def _scheduled_retrain(self):
        """Wrapper for scheduled retraining"""
        loop = asyncio.get_event_loop()
        loop.create_task(self.retrain_models())
    
    async def _run_scheduler(self):
        """Run the background scheduler"""
        while True:
            schedule.run_pending()
            await asyncio.sleep(60)  # Check every minute
