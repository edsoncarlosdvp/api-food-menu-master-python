from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# Database connection parameters
DB_USER = os.getenv("DB_USER", "sa")
DB_PASSWORD = os.getenv("DB_PASSWORD", "root")
DB_HOST = os.getenv("DB_HOST", "sqlserver")
DB_PORT = os.getenv("DB_PORT", "1433")
DB_NAME = os.getenv("DB_NAME", "food_menu_db")

# SQL Server connection string
# Format: mssql+pyodbc://user:password@host:port/database?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes
DATABASE_URL = (
    f"mssql+pyodbc://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    f"?driver=ODBC+Driver+18+for+SQL+Server&TrustServerCertificate=yes"
)

# Create SQLAlchemy engine
# poolclass=NullPool: Disables connection pooling (useful for containerized apps)
# echo=True: Logs SQL queries (useful for debugging, set to False in production)
engine = create_engine(
    DATABASE_URL,
    poolclass=NullPool,
    echo=True  # Set to False in production
)

# Create SessionLocal class - each instance is a database session
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """
    Dependency function to get database session.
    
    This function is used with FastAPI's dependency injection.
    It creates a new database session for each request and closes it after.
    
    Usage in endpoints:
        @app.get("/items")
        def read_items(db: Session = Depends(get_db)):
            ...
    
    Yields:
        Session: Database session
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """
    Initialize database - create all tables.
    
    This function should be called once when the application starts.
    It creates all tables defined in models.py if they don't exist.
    """
    from app.models import Base
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")