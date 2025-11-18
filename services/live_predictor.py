"""
Live Race Prediction Service
Real-time F1 race outcome predictions during live races
"""

import asyncio
import websockets
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import aiohttp
from dataclasses import dataclass

from app.ml.predictor import RacePredictor
from app.core.config import settings
from app.core.logging import setup_logging

logger = setup_logging()

@dataclass
class LiveRaceData:
    """Live race data structure"""
    race_id: str
    current_lap: int
    total_laps: int
    positions: List[Dict]
    lap_times: Dict[str, List[float]]
    tire_data: Dict[str, Dict]
    weather: Dict[str, Any]
    safety_car: bool
    timestamp: datetime

class LivePredictionService:
    """Service for real-time race predictions"""
    
    def __init__(self):
        self.predictor = RacePredictor()
        self.active_races = {}
        self.websocket_clients = set()
        self.prediction_interval = settings.LIVE_PREDICTION_INTERVAL
        self.data_refresh_rate = settings.RACE_DATA_REFRESH_RATE
        
    async def start_service(self):
        """Start the live prediction service"""
        try:
            logger.info("🚀 Starting Live Race Prediction Service...")
            
            # Load ML models
            await self.predictor.load_race_data
            
            # Start WebSocket server
            websocket_server = await websockets.serve(
                self.handle_websocket_connection,
                settings.WS_HOST,
                settings.WS_PORT
            )
            
            logger.info(f"📡 WebSocket server started on {settings.WS_HOST}:{settings.WS_PORT}")
            
            # Start background tasks
            asyncio.create_task(self.monitor_active_races())
            asyncio.create_task(self.periodic_predictions())
            
            logger.info("✅ Live Prediction Service is running!")
            
            # Keep the service running
            await websocket_server.wait_closed()
            
        except Exception as e:
            logger.error(f"❌ Failed to start Live Prediction Service: {e}")
            raise
    
    async def start_live_predictions(self, race_id: str):
        """Start live predictions for a specific race"""
        try:
            logger.info(f"🏁 Starting live predictions for {race_id}")
            
            # Initialize race monitoring
            self.active_races[race_id] = {
                'status': 'active',
                'start_time': datetime.utcnow(),
                'last_prediction': None,
                'prediction_count': 0
            }
            
            # Start race-specific monitoring
            asyncio.create_task(self.monitor_race(race_id))
            
            logger.info(f"✅ Live predictions started for {race_id}")
            
        except Exception as e:
            logger.error(f"❌ Failed to start live predictions for {race_id}: {e}")
            raise
    
    async def stop_live_predictions(self, race_id: str):
        """Stop live predictions for a specific race"""
        try:
            if race_id in self.active_races:
                self.active_races[race_id]['status'] = 'stopped'
                logger.info(f"🏁 Stopped live predictions for {race_id}")
            
        except Exception as e:
            logger.error(f"Failed to stop live predictions for {race_id}: {e}")
    
    async def monitor_race(self, race_id: str):
        """Monitor a specific race and generate predictions"""
        try:
            while self.active_races.get(race_id, {}).get('status') == 'active':
                # Get live race data
                live_data = await self.get_live_race_data(race_id)
                
                if live_data:
                    # Generate predictions
                    predictions = await self.generate_live_predictions(live_data)
                    
                    # Store prediction
                    self.active_races[race_id]['last_prediction'] = predictions
                    self.active_races[race_id]['prediction_count'] += 1
                    
                    # Broadcast to WebSocket clients
                    await self.broadcast_predictions(race_id, predictions)
                    
                    # Log prediction
                    logger.info(f"📊 Generated prediction #{self.active_races[race_id]['prediction_count']} for {race_id}")
                
                # Wait before next prediction
                await asyncio.sleep(self.prediction_interval)
                
        except Exception as e:
            logger.error(f"Race monitoring failed for {race_id}: {e}")
    
    async def get_live_race_data(self, race_id: str) -> Optional[LiveRaceData]:
        """Fetch live race data from F1 timing API"""
        try:
            # This would integrate with actual F1 live timing API
            # For now, return mock data
            
            current_time = datetime.utcnow()
            
            # Mock live race data
            live_data = LiveRaceData(
                race_id=race_id,
                current_lap=min(45, int((current_time.minute % 60) + 1)),
                total_laps=58,
                positions=[
                    {"position": 1, "driver": "Max Verstappen", "gap": "0.000", "interval": "0.000"},
                    {"position": 2, "driver": "Lewis Hamilton", "gap": "5.234", "interval": "5.234"},
                    {"position": 3, "driver": "Charles Leclerc", "gap": "12.567", "interval": "7.333"},
                    {"position": 4, "driver": "Lando Norris", "gap": "18.890", "interval": "6.323"},
                    {"position": 5, "driver": "George Russell", "gap": "25.123", "interval": "6.233"}
                ],
                lap_times={
                    "verstappen": [92.345, 91.234, 90.987, 91.456],
                    "hamilton": [92.567, 91.789, 91.234, 91.678],
                    "leclerc": [93.123, 92.456, 91.789, 92.123]
                },
                tire_data={
                    "verstappen": {"compound": "medium", "age": 15, "pit_stops": 1},
                    "hamilton": {"compound": "hard", "age": 8, "pit_stops": 1},
                    "leclerc": {"compound": "medium", "age": 12, "pit_stops": 1}
                },
                weather={
                    "temperature": 28.5,
                    "humidity": 45,
                    "wind_speed": 12.3,
                    "precipitation": False
                },
                safety_car=False,
                timestamp=current_time
            )
            
            return live_data
            
        except Exception as e:
            logger.error(f"Failed to get live race data for {race_id}: {e}")
            return None
    
    async def generate_live_predictions(self, live_data: LiveRaceData) -> Dict[str, Any]:
        """Generate live race predictions"""
        try:
            # Convert to format expected by predictor
            live_data_dict = {
                'race_id': live_data.race_id,
                'current_lap': live_data.current_lap,
                'total_laps': live_data.total_laps,
                'positions': live_data.positions,
                'lap_times': live_data.lap_times,
                'tire_data': live_data.tire_data,
                'weather': live_data.weather,
                'safety_car': live_data.safety_car,
                'timestamp': live_data.timestamp
            }
            
            # Generate predictions
            predictions = await self.predictor.predict_live_race_outcome(live_data_dict)
            
            # Add metadata
            predictions['race_id'] = live_data.race_id
            predictions['current_lap'] = live_data.current_lap
            predictions['race_progress'] = live_data.current_lap / live_data.total_laps
            predictions['timestamp'] = live_data.timestamp.isoformat()
            
            return predictions
            
        except Exception as e:
            logger.error(f"Failed to generate live predictions: {e}")
            return {
                'error': str(e),
                'race_id': live_data.race_id if live_data else 'unknown',
                'timestamp': datetime.utcnow().isoformat()
            }
    
    async def handle_websocket_connection(self, websocket, path):
        """Handle WebSocket client connections"""
        try:
            logger.info(f"📱 New WebSocket client connected: {websocket.remote_address}")
            self.websocket_clients.add(websocket)
            
            # Send welcome message
            welcome_message = {
                'type': 'welcome',
                'message': 'Connected to F1 Live Predictions',
                'active_races': list(self.active_races.keys()),
                'timestamp': datetime.utcnow().isoformat()
            }
            await websocket.send(json.dumps(welcome_message))
            
            # Handle incoming messages
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': 'Invalid JSON format'
                    }))
                    
        except websockets.exceptions.ConnectionClosed:
            logger.info("📱 WebSocket client disconnected")
        except Exception as e:
            logger.error(f"WebSocket connection error: {e}")
        finally:
            self.websocket_clients.discard(websocket)
    
    async def handle_client_message(self, websocket, data: Dict[str, Any]):
        """Handle messages from WebSocket clients"""
        try:
            message_type = data.get('type')
            
            if message_type == 'subscribe':
                race_id = data.get('race_id')
                if race_id in self.active_races:
                    # Send latest prediction for this race
                    latest_prediction = self.active_races[race_id].get('last_prediction')
                    if latest_prediction:
                        response = {
                            'type': 'prediction',
                            'race_id': race_id,
                            'data': latest_prediction
                        }
                        await websocket.send(json.dumps(response))
                else:
                    await websocket.send(json.dumps({
                        'type': 'error',
                        'message': f'Race {race_id} not found or not active'
                    }))
            
            elif message_type == 'get_active_races':
                response = {
                    'type': 'active_races',
                    'races': list(self.active_races.keys()),
                    'timestamp': datetime.utcnow().isoformat()
                }
                await websocket.send(json.dumps(response))
            
        except Exception as e:
            logger.error(f"Error handling client message: {e}")
            await websocket.send(json.dumps({
                'type': 'error',
                'message': 'Internal server error'
            }))
    
    async def broadcast_predictions(self, race_id: str, predictions: Dict[str, Any]):
        """Broadcast predictions to all connected WebSocket clients"""
        try:
            if not self.websocket_clients:
                return
            
            message = {
                'type': 'prediction',
                'race_id': race_id,
                'data': predictions
            }
            
            # Send to all connected clients
            disconnected_clients = set()
            for client in self.websocket_clients:
                try:
                    await client.send(json.dumps(message))
                except websockets.exceptions.ConnectionClosed:
                    disconnected_clients.add(client)
                except Exception as e:
                    logger.warning(f"Failed to send to client: {e}")
                    disconnected_clients.add(client)
            
            # Remove disconnected clients
            self.websocket_clients -= disconnected_clients
            
        except Exception as e:
            logger.error(f"Failed to broadcast predictions: {e}")
    
    async def monitor_active_races(self):
        """Monitor all active races for status changes"""
        try:
            while True:
                current_time = datetime.utcnow()
                
                # Check each active race
                for race_id, race_info in list(self.active_races.items()):
                    # Check if race has been running too long (cleanup)
                    if race_info['status'] == 'active':
                        runtime = current_time - race_info['start_time']
                        if runtime > timedelta(hours=4):  # Max race duration
                            logger.info(f"🏁 Auto-stopping race {race_id} after 4 hours")
                            await self.stop_live_predictions(race_id)
                
                await asyncio.sleep(60)  # Check every minute
                
        except Exception as e:
            logger.error(f"Race monitoring failed: {e}")
    
    async def periodic_predictions(self):
        """Generate periodic predictions for all active races"""
        try:
            while True:
                for race_id in list(self.active_races.keys()):
                    if self.active_races[race_id]['status'] == 'active':
                        # This is handled by individual race monitors
                        pass
                
                await asyncio.sleep(self.prediction_interval)
                
        except Exception as e:
            logger.error(f"Periodic predictions failed: {e}")
    
    def get_service_status(self) -> Dict[str, Any]:
        """Get current service status"""
        return {
            'status': 'running',
            'active_races': len(self.active_races),
            'connected_clients': len(self.websocket_clients),
            'races': {
                race_id: {
                    'status': info['status'],
                    'runtime': str(datetime.utcnow() - info['start_time']),
                    'predictions_generated': info['prediction_count']
                }
                for race_id, info in self.active_races.items()
            },
            'timestamp': datetime.utcnow().isoformat()
        }

# Main entry point
async def main():
    """Main entry point for the live prediction service"""
    service = LivePredictionService()
    
    try:
        await service.start_service()
    except KeyboardInterrupt:
        logger.info("🛑 Live Prediction Service stopped by user")
    except Exception as e:
        logger.error(f"❌ Live Prediction Service failed: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
