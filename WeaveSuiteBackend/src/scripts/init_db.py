from db.database import Base, engine
from sqlalchemy import inspect
import logging

def init_db():
    """Initialize database tables if they don't exist"""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            Base.metadata.create_all(bind=engine)
            #logging.debug("Database tables created successfully")
        #else:
            #logging.debug("Database tables already exist")
    except Exception as e:
        logging.error(f"ERROR initializing database: {e}")
        raise

if __name__ == "__main__":
    init_db()