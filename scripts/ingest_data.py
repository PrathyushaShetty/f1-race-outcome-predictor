import fastf1
import pandas as pd
import os
from datetime import datetime
import logging
import warnings

# Suppress FutureWarnings from pandas/fastf1
warnings.simplefilter(action='ignore', category=FutureWarning)

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Create data directory
DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

# Enable cache for fastf1
CACHE_DIR = "data/cache"
os.makedirs(CACHE_DIR, exist_ok=True)
fastf1.Cache.enable_cache(CACHE_DIR)

def fetch_season_data(year):
    """Fetch and process data for a specific season"""
    logger.info(f"Fetching data for season {year}...")
    
    try:
        schedule = fastf1.get_event_schedule(year)
        season_data = []
        
        for _, event in schedule.iterrows():
            # Skip testing sessions
            if event['EventFormat'] == 'testing':
                continue
                
            round_number = event['RoundNumber']
            event_name = event['EventName']
            country = event['Country']
            location = event['Location']
            
            logger.info(f"Processing Round {round_number}: {event_name}")
            
            try:
                # Load Race Session
                session = fastf1.get_session(year, round_number, 'R')
                session.load(telemetry=False, weather=True, messages=False)
                
                # Get Race Results
                results = session.results
                
                # Get Weather Data (Average for the session)
                weather = session.weather_data
                avg_air_temp = weather['AirTemp'].mean() if not weather.empty else None
                avg_track_temp = weather['TrackTemp'].mean() if not weather.empty else None
                rain_probability = weather['Rainfall'].mean() if not weather.empty else 0 # Binary in fastf1, so mean is % of time raining
                
                # Process each driver's result
                for driver_code, row in results.iterrows():
                    driver_data = {
                        'season': year,
                        'round': round_number,
                        'circuit_name': event_name,
                        'country': country,
                        'location': location,
                        'date': event['EventDate'],
                        
                        # Driver Info
                        'driver_code': driver_code,
                        'driver_number': row['DriverNumber'],
                        'team': row['TeamName'],
                        
                        # Qualifying/Grid
                        'grid_position': row['GridPosition'],
                        
                        # Race Result
                        'position': row['Position'],
                        'points': row['Points'],
                        'status': row['Status'],
                        
                        # Performance Metrics
                        'laps_completed': row['Laps'], # Use 'Laps' instead of len(session.laps...) for safety
                        
                        # Weather
                        'air_temp': avg_air_temp,
                        'track_temp': avg_track_temp,
                        'rain_probability': rain_probability
                    }
                    
                    # Add to season list
                    season_data.append(driver_data)
                    
            except Exception as e:
                logger.error(f"Error processing {event_name}: {e}")
                continue
                
        return pd.DataFrame(season_data)
        
    except Exception as e:
        logger.error(f"Error fetching season {year}: {e}")
        return pd.DataFrame()

def main():
    # Define years to fetch
    years = [2021, 2022, 2023]
    
    all_data = []
    
    for year in years:
        df = fetch_season_data(year)
        if not df.empty:
            all_data.append(df)
            
    if all_data:
        final_df = pd.concat(all_data, ignore_index=True)
        
        # Save to CSV
        output_file = os.path.join(DATA_DIR, "f1_historical_data.csv")
        final_df.to_csv(output_file, index=False)
        logger.info(f"Successfully saved {len(final_df)} rows to {output_file}")
        
        # Display sample
        print("\nData Sample:")
        print(final_df.head())
        print("\nColumns:")
        print(final_df.columns.tolist())
    else:
        logger.warning("No data collected.")

if __name__ == "__main__":
    main()
