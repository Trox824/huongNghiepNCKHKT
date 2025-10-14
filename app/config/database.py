"""
Database configuration and connection management
"""
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import streamlit as st

# PostgreSQL connection URL
DATABASE_URL = "postgresql://postgres:etJtdOhpsVUCwGoOsDlyXzTsXGNFvAdS@shinkansen.proxy.rlwy.net:51402/railway"

# Create SQLAlchemy engine
engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,  # Enable connection health checks
    pool_size=10,
    max_overflow=20,
    echo=False  # Set to True for SQL logging
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create Base class for models
Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database tables"""
    from app.database.models import Student, Grade, Prediction, Framework, AssessmentResponse, CareerRecommendation
    
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

@st.cache_resource
def get_session_factory():
    """Get cached session factory for Streamlit"""
    return SessionLocal

def get_db_connection():
    """Get fresh database connection for Streamlit"""
    # Get or create a new session for this request
    session_factory = get_session_factory()
    return session_factory()

