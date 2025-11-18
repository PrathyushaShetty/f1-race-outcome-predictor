"""
Database configuration and connection management
"""

from sqlalchemy import create_engine, MetaData
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import asyncpg
import asyncio

from app.core.config import settings

# Create SQLAlchemy engine
engine = create_engine(
    settings.DATABASE_URL,
    poolclass=StaticPool,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300
)

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create declarative base
Base = declarative_base()

# Metadata for database operations
metadata = MetaData()


async def init_db():
    """Initialize database and create tables"""
    try:
        # Create database if it doesn't exist
        await create_database_if_not_exists()
        
        # Create all tables
        Base.metadata.create_all(bind=engine)
        
        return True
    except Exception as e:
        raise Exception(f"Database initialization failed: {e}")


async def create_database_if_not_exists():
    """Create database if it doesn't exist"""
    try:
        # Parse database URL to get connection details
        db_url_parts = settings.DATABASE_URL.replace("postgresql://", "").split("/")
        connection_part = db_url_parts[0]
        database_name = db_url_parts[1] if len(db_url_parts) > 1 else settings.DATABASE_NAME
        
        user_pass, host_port = connection_part.split("@")
        user, password = user_pass.split(":")
        host, port = host_port.split(":")
        
        # Connect to PostgreSQL server (not specific database)
        conn = await asyncpg.connect(
            host=host,
            port=int(port),
            user=user,
            password=password,
            database="postgres"  # Connect to default postgres database
        )
        
        # Check if database exists
        result = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", database_name
        )
        
        if not result:
            # Create database
            await conn.execute(f'CREATE DATABASE "{database_name}"')
            print(f"✅ Database '{database_name}' created successfully")
        
        await conn.close()
        
    except Exception as e:
        print(f"⚠️ Database creation check failed: {e}")


def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


class DatabaseManager:
    """Database manager for connection handling"""
    
    def __init__(self):
        self.engine = engine
        self.SessionLocal = SessionLocal
    
    def get_session(self):
        """Get a database session"""
        return self.SessionLocal()
    
    def close_session(self, session):
        """Close a database session"""
        session.close()
    
    async def health_check(self):
        """Check database health"""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception:
            return False
