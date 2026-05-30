import os
import sys
from contextlib import contextmanager
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#load environment variables from the .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

#database configuration
POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "secret")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")
POSTGRES_DB = os.getenv("POSTGRES_DB")

DATABASE_URL = f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=40, #20 + 40 = 60 concurrent connections max
    pool_recycle=300, #SQLAlchemy will recycle connections older than 5 minutes. protects against idle-connection timeouts on the DB side
    pool_pre_ping=True, #validate connection liveness before each checkout
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()
print("Declarative base created")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@contextmanager
def db_session():
    """Context manager for use OUTSIDE FastAPI's dependency system background-task workers, startup hooks, scripts, anywhere the
    request lifecycle doesn't apply. each call creates a session, yields it, rolls back on exception, and always closes.
    """
    print("db_session called - creating new database session")
    db = SessionLocal()
    try:
        yield db
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()