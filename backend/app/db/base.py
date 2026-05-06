from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Create the database engine using the connection URL from settings
# The engine manages the actual connection to PostgreSQL
engine = create_engine(settings.DATABASE_URL)

# Create a session factory with the following settings:
# autocommit=False — changes are NOT saved automatically, we call commit() manually
# autoflush=False  — changes are NOT sent to DB before each query automatically
# bind=engine      — connect this session factory to our PostgreSQL engine
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for all database models (Product, PriceHistory, Alert)
# Every model that inherits from Base will be registered as a database table
class Base(DeclarativeBase):
    pass

# Dependency function that provides a database session for each HTTP request
# Used with FastAPI's Depends() mechanism in route handlers
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
