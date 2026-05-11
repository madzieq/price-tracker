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

def get_db():
    """ Provide a database session for each HTTP request.

    Used as a FastAPI dependency via Depends(get_db) in route handlers.
    Ensures the session is always closed after the request, even if an error occurs.

    Yields:
        Session: an active SQLAlchemy database session
    Example:
        @router.get("/products")
        def list_products(db: Session = Depends(get_db)):
            return db.query(Product).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
