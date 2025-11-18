"""
Database initialization script for F1 Race Outcome Predictor
"""

import asyncio
import sys
import os
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base, init_db
from app.core.config import settings
from app.core.logging import setup_logging

logger = setup_logging()

# Database Models
class Driver(Base):
    """Driver model"""
    __tablename__ = "drivers"
    
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    code = Column(String, index=True)
    nationality = Column(String)
    date_of_birth = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Constructor(Base):
    """Constructor/Team model"""
    __tablename__ = "constructors"
    
    id = Column(Integer, primary_key=True, index=True)
    constructor_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    nationality = Column(String)
    url = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Circuit(Base):
    """Circuit model"""
    __tablename__ = "circuits"
    
    id = Column(Integer, primary_key=True, index=True)
    circuit_id = Column(String, unique=True, index=True)
    name = Column(String, index=True)
    location = Column(String)
    country = Column(String)
    latitude = Column(Float)
    longitude = Column(Float)
    length = Column(Float)
    turns = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Race(Base):
    """Race model"""
    __tablename__ = "races"
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(String, unique=True, index=True)
    season = Column(Integer, index=True)
    round = Column(Integer)
    name = Column(String, index=True)
    circuit_id = Column(String, ForeignKey("circuits.circuit_id"))
    date = Column(String)
    time = Column(String)
    status = Column(String, default="scheduled")  # scheduled, active, completed
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    circuit = relationship("Circuit")

class RaceResult(Base):
    """Race result model"""
    __tablename__ = "race_results"
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(String, ForeignKey("races.race_id"))
    driver_id = Column(String, ForeignKey("drivers.driver_id"))
    constructor_id = Column(String, ForeignKey("constructors.constructor_id"))
    position = Column(Integer)
    points = Column(Float)
    laps = Column(Integer)
    time = Column(String)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    race = relationship("Race")
    driver = relationship("Driver")
    constructor = relationship("Constructor")

class Prediction(Base):
    """Prediction model"""
    __tablename__ = "predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String, unique=True, index=True)
    race_id = Column(String, ForeignKey("races.race_id"))
    prediction_type = Column(String)  # pre_race, live, podium
    predicted_winner = Column(String)
    predicted_top_3 = Column(Text)  # JSON string
    confidence = Column(Float)
    model_version = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    race = relationship("Race")

class FanPrediction(Base):
    """Fan prediction model"""
    __tablename__ = "fan_predictions"
    
    id = Column(Integer, primary_key=True, index=True)
    prediction_id = Column(String, unique=True, index=True)
    user_id = Column(String, index=True)
    race_id = Column(String, ForeignKey("races.race_id"))
    predicted_winner = Column(String)
    predicted_podium = Column(Text)  # JSON string
    confidence = Column(Float)
    reasoning = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    race = relationship("Race")

class ModelPerformance(Base):
    """Model performance tracking"""
    __tablename__ = "model_performance"
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(String, ForeignKey("races.race_id"))
    model_name = Column(String)
    model_version = Column(String)
    accuracy = Column(Float)
    precision = Column(Float)
    recall = Column(Float)
    f1_score = Column(Float)
    confidence_calibration = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    race = relationship("Race")

class WeatherData(Base):
    """Weather data model"""
    __tablename__ = "weather_data"
    
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(String, ForeignKey("races.race_id"))
    temperature = Column(Float)
    humidity = Column(Float)
    wind_speed = Column(Float)
    precipitation = Column(Boolean)
    conditions = Column(String)
    forecast_time = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    race = relationship("Race")

async def create_tables():
    """Create all database tables"""
    try:
        logger.info("🗄️ Creating database tables...")
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        logger.info("✅ Database tables created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create tables: {e}")
        raise

async def populate_sample_data():
    """Populate database with sample data"""
    try:
        logger.info("📊 Populating sample data...")
        
        from app.core.database import SessionLocal
        
        db = SessionLocal()
        
        # Sample circuits
        circuits = [
            Circuit(
                circuit_id="bahrain",
                name="Bahrain International Circuit",
                location="Sakhir",
                country="Bahrain",
                latitude=26.0325,
                longitude=50.5106,
                length=5.412,
                turns=15
            ),
            Circuit(
                circuit_id="monaco",
                name="Circuit de Monaco",
                location="Monte Carlo",
                country="Monaco",
                latitude=43.7347,
                longitude=7.4206,
                length=3.337,
                turns=19
            ),
            Circuit(
                circuit_id="silverstone",
                name="Silverstone Circuit",
                location="Silverstone",
                country="United Kingdom",
                latitude=52.0786,
                longitude=-1.0169,
                length=5.891,
                turns=18
            )
        ]
        
        # Sample drivers
        drivers = [
            Driver(
                driver_id="max_verstappen",
                name="Max Verstappen",
                code="VER",
                nationality="Dutch",
                date_of_birth="1997-09-30"
            ),
            Driver(
                driver_id="lewis_hamilton",
                name="Lewis Hamilton",
                code="HAM",
                nationality="British",
                date_of_birth="1985-01-07"
            ),
            Driver(
                driver_id="charles_leclerc",
                name="Charles Leclerc",
                code="LEC",
                nationality="Monégasque",
                date_of_birth="1997-10-16"
            ),
            Driver(
                driver_id="lando_norris",
                name="Lando Norris",
                code="NOR",
                nationality="British",
                date_of_birth="1999-11-13"
            ),
            Driver(
                driver_id="george_russell",
                name="George Russell",
                code="RUS",
                nationality="British",
                date_of_birth="1998-02-15"
            )
        ]
        
        # Sample constructors
        constructors = [
            Constructor(
                constructor_id="red_bull",
                name="Red Bull Racing",
                nationality="Austrian",
                url="http://www.redbullracing.com/"
            ),
            Constructor(
                constructor_id="mercedes",
                name="Mercedes",
                nationality="German",
                url="http://www.mercedesamgf1.com/"
            ),
            Constructor(
                constructor_id="ferrari",
                name="Ferrari",
                nationality="Italian",
                url="http://www.ferrari.com/"
            ),
            Constructor(
                constructor_id="mclaren",
                name="McLaren",
                nationality="British",
                url="http://www.mclaren.com/"
            )
        ]
        
        # Sample races
        races = [
            Race(
                race_id="bahrain-2024",
                season=2024,
                round=1,
                name="Bahrain Grand Prix",
                circuit_id="bahrain",
                date="2024-03-02",
                time="15:00:00Z"
            ),
            Race(
                race_id="monaco-2024",
                season=2024,
                round=8,
                name="Monaco Grand Prix",
                circuit_id="monaco",
                date="2024-05-26",
                time="13:00:00Z"
            )
        ]
        
        # Add all sample data
        for circuit in circuits:
            db.merge(circuit)
        
        for driver in drivers:
            db.merge(driver)
        
        for constructor in constructors:
            db.merge(constructor)
        
        for race in races:
            db.merge(race)
        
        db.commit()
        db.close()
        
        logger.info("✅ Sample data populated successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to populate sample data: {e}")
        if 'db' in locals():
            db.rollback()
            db.close()
        raise

async def create_indexes():
    """Create database indexes for performance"""
    try:
        logger.info("📈 Creating database indexes...")
        
        # This would create additional indexes for performance
        # For now, indexes are created with the table definitions
        
        logger.info("✅ Database indexes created successfully")
        
    except Exception as e:
        logger.error(f"❌ Failed to create indexes: {e}")
        raise

async def main():
    """Main database initialization function"""
    try:
        logger.info("🚀 Starting database initialization...")
        
        # Initialize database connection
        await init_db()
        
        # Create tables
        await create_tables()
        
        # Create indexes
        await create_indexes()
        
        # Populate sample data
        await populate_sample_data()
        
        logger.info("✅ Database initialization completed successfully!")
        
        # Print summary
        print("\n" + "="*50)
        print("🏎️  F1 RACE OUTCOME PREDICTOR DATABASE")
        print("="*50)
        print(f"📊 Database URL: {settings.DATABASE_URL}")
        print(f"🗄️  Tables created: 8")
        print(f"📈 Indexes created: Multiple")
        print(f"🎯 Sample data: Populated")
        print("="*50)
        print("✅ Database is ready for use!")
        print("="*50)
        
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        print(f"\n❌ Database initialization failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
