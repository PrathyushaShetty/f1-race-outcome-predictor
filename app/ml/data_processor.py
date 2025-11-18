"""
Data processing module for F1 prediction system
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
import asyncio
import aiohttp
from datetime import datetime, timedelta

from app.core.config import settings
from app.core.logging import setup_logging

logger = setup_logging()

class DataProcessor:
    """Handles data loading and preprocessing from various sources"""
    
    def __init__(self):
        self.ergast_base_url = settings.ERGAST_API_BASE_URL
        self.cache_enabled = settings.ERGAST_CACHE_ENABLED
        
    async def load_historical_data(self, circuit: str, year: str) -> Dict[str, Any]:
        """Load historical race data for a specific circuit"""
        try:
            logger.info(f"Loading historical data for {circuit} circuit")
            
            # Load race results from Ergast API
            race_results = await self._fetch_ergast_data(
                f"circuits/{circuit}/results.json?limit=1000"
            )
            
            # Load qualifying results
            qualifying_results = await self._fetch_ergast_data(
                f"circuits/{circuit}/qualifying.json?limit=1000"
            )
            
            # Process and combine data
            processed_data = self._process_historical_results(race_results, qualifying_results)
            
            return {
                'circuit': circuit,
                'race_results': processed_data['races'],
                'qualifying_results': processed_data['qualifying'],
                'statistics': processed_data['stats']
            }
            
        except Exception as e:
            logger.error(f"Failed to load historical data: {e}")
            return {}
    
    async def load_current_season_data(self, year: str) -> Dict[str, Any]:
        """Load current season data including standings and recent results"""
        try:
            logger.info(f"Loading current season data for {year}")
            
            # Load driver standings
            driver_standings = await self._fetch_ergast_data(
                f"{year}/driverStandings.json"
            )
            
            # Load constructor standings
            constructor_standings = await self._fetch_ergast_data(
                f"{year}/constructorStandings.json"
            )
            
            # Load recent race results
            recent_results = await self._fetch_ergast_data(
                f"{year}/results.json?limit=100"
            )
            
            return {
                'year': year,
                'driver_standings': self._process_standings(driver_standings, 'drivers'),
                'constructor_standings': self._process_standings(constructor_standings, 'constructors'),
                'recent_results': self._process_recent_results(recent_results)
            }
            
        except Exception as e:
            logger.error(f"Failed to load current season data: {e}")
            return {}
    
    async def load_driver_data(self, year: str) -> Dict[str, Any]:
        """Load comprehensive driver data and statistics"""
        try:
            logger.info(f"Loading driver data for {year}")
            
            # Load driver list
            drivers = await self._fetch_ergast_data(f"{year}/drivers.json")
            
            # Process driver information
            driver_data = []
            for driver_info in drivers.get('MRData', {}).get('DriverTable', {}).get('Drivers', []):
                driver_stats = await self._calculate_driver_statistics(driver_info, year)
                driver_data.append({
                    'driver_id': driver_info.get('driverId'),
                    'name': f"{driver_info.get('givenName')} {driver_info.get('familyName')}",
                    'code': driver_info.get('code'),
                    'nationality': driver_info.get('nationality'),
                    'date_of_birth': driver_info.get('dateOfBirth'),
                    'statistics': driver_stats
                })
            
            return {
                'year': year,
                'drivers': driver_data,
                'total_drivers': len(driver_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to load driver data: {e}")
            return {'drivers': []}
    
    async def load_team_data(self, year: str) -> Dict[str, Any]:
        """Load team/constructor data and performance metrics"""
        try:
            logger.info(f"Loading team data for {year}")
            
            # Load constructor data
            constructors = await self._fetch_ergast_data(f"{year}/constructors.json")
            
            # Process team information
            team_data = []
            for constructor in constructors.get('MRData', {}).get('ConstructorTable', {}).get('Constructors', []):
                team_stats = await self._calculate_team_statistics(constructor, year)
                team_data.append({
                    'constructor_id': constructor.get('constructorId'),
                    'name': constructor.get('name'),
                    'nationality': constructor.get('nationality'),
                    'url': constructor.get('url'),
                    'statistics': team_stats
                })
            
            return {
                'year': year,
                'teams': team_data,
                'total_teams': len(team_data)
            }
            
        except Exception as e:
            logger.error(f"Failed to load team data: {e}")
            return {'teams': []}
    
    async def load_session_data(self, race_id: str) -> Dict[str, Any]:
        """Load practice and qualifying session data"""
        try:
            logger.info(f"Loading session data for {race_id}")
            
            # Parse race info
            race_info = self._parse_race_id(race_id)
            year = race_info['year']
            circuit = race_info['circuit']
            
            # This would integrate with FastF1 for detailed session data
            # For now, return mock structure
            return {
                'practice_sessions': {
                    'fp1': {'available': False, 'data': {}},
                    'fp2': {'available': False, 'data': {}},
                    'fp3': {'available': False, 'data': {}}
                },
                'qualifying': {'available': False, 'data': {}},
                'sprint': {'available': False, 'data': {}}
            }
            
        except Exception as e:
            logger.error(f"Failed to load session data: {e}")
            return {}
    
    async def _fetch_ergast_data(self, endpoint: str) -> Dict[str, Any]:
        """Fetch data from Ergast API"""
        try:
            url = f"{self.ergast_base_url}/{endpoint}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data
                    else:
                        logger.error(f"Ergast API error: {response.status}")
                        return {}
                        
        except Exception as e:
            logger.error(f"Failed to fetch Ergast data: {e}")
            return {}
    
    def _process_historical_results(self, race_results: Dict, qualifying_results: Dict) -> Dict[str, Any]:
        """Process historical race and qualifying results"""
        try:
            races = []
            qualifying = []
            
            # Process race results
            race_data = race_results.get('MRData', {}).get('RaceTable', {}).get('Races', [])
            for race in race_data:
                processed_race = {
                    'season': race.get('season'),
                    'round': race.get('round'),
                    'race_name': race.get('raceName'),
                    'date': race.get('date'),
                    'results': race.get('Results', [])
                }
                races.append(processed_race)
            
            # Process qualifying results
            qual_data = qualifying_results.get('MRData', {}).get('RaceTable', {}).get('Races', [])
            for race in qual_data:
                processed_qual = {
                    'season': race.get('season'),
                    'round': race.get('round'),
                    'race_name': race.get('raceName'),
                    'date': race.get('date'),
                    'qualifying_results': race.get('QualifyingResults', [])
                }
                qualifying.append(processed_qual)
            
            # Calculate statistics
            stats = self._calculate_historical_statistics(races, qualifying)
            
            return {
                'races': races,
                'qualifying': qualifying,
                'stats': stats
            }
            
        except Exception as e:
            logger.error(f"Failed to process historical results: {e}")
            return {'races': [], 'qualifying': [], 'stats': {}}
    
    def _process_standings(self, standings_data: Dict, standings_type: str) -> List[Dict]:
        """Process driver or constructor standings"""
        try:
            standings = []
            
            if standings_type == 'drivers':
                standings_list = standings_data.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
                if standings_list:
                    for standing in standings_list[0].get('DriverStandings', []):
                        standings.append({
                            'position': int(standing.get('position', 0)),
                            'points': float(standing.get('points', 0)),
                            'wins': int(standing.get('wins', 0)),
                            'driver': standing.get('Driver', {}),
                            'constructors': standing.get('Constructors', [])
                        })
            
            elif standings_type == 'constructors':
                standings_list = standings_data.get('MRData', {}).get('StandingsTable', {}).get('StandingsLists', [])
                if standings_list:
                    for standing in standings_list[0].get('ConstructorStandings', []):
                        standings.append({
                            'position': int(standing.get('position', 0)),
                            'points': float(standing.get('points', 0)),
                            'wins': int(standing.get('wins', 0)),
                            'constructor': standing.get('Constructor', {})
                        })
            
            return standings
            
        except Exception as e:
            logger.error(f"Failed to process standings: {e}")
            return []
    
    def _process_recent_results(self, results_data: Dict) -> List[Dict]:
        """Process recent race results"""
        try:
            results = []
            races = results_data.get('MRData', {}).get('RaceTable', {}).get('Races', [])
            
            for race in races:
                race_results = {
                    'season': race.get('season'),
                    'round': race.get('round'),
                    'race_name': race.get('raceName'),
                    'date': race.get('date'),
                    'circuit': race.get('Circuit', {}),
                    'results': race.get('Results', [])
                }
                results.append(race_results)
            
            return results
            
        except Exception as e:
            logger.error(f"Failed to process recent results: {e}")
            return []
    
    async def _calculate_driver_statistics(self, driver_info: Dict, year: str) -> Dict[str, Any]:
        """Calculate comprehensive driver statistics"""
        try:
            # This would calculate detailed driver statistics
            # For now, return basic structure
            return {
                'races_entered': 0,
                'wins': 0,
                'podiums': 0,
                'points': 0.0,
                'avg_finish_position': 0.0,
                'dnf_rate': 0.0,
                'qualifying_avg': 0.0,
                'form_trend': 'stable'
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate driver statistics: {e}")
            return {}
    
    async def _calculate_team_statistics(self, constructor_info: Dict, year: str) -> Dict[str, Any]:
        """Calculate comprehensive team statistics"""
        try:
            # This would calculate detailed team statistics
            # For now, return basic structure
            return {
                'races_entered': 0,
                'wins': 0,
                'podiums': 0,
                'points': 0.0,
                'avg_finish_position': 0.0,
                'reliability_rate': 0.0,
                'development_trend': 'stable'
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate team statistics: {e}")
            return {}
    
    def _calculate_historical_statistics(self, races: List[Dict], qualifying: List[Dict]) -> Dict[str, Any]:
        """Calculate historical statistics for the circuit"""
        try:
            return {
                'total_races': len(races),
                'pole_position_advantage': 0.65,
                'overtaking_frequency': 0.25,
                'safety_car_probability': 0.35,
                'weather_impact': 'medium',
                'tire_degradation': 'high'
            }
            
        except Exception as e:
            logger.error(f"Failed to calculate historical statistics: {e}")
            return {}
    
    def _parse_race_id(self, race_id: str) -> Dict[str, str]:
        """Parse race ID to extract information"""
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
