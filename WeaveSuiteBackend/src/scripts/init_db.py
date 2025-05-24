from db.database import Base, engine
from sqlalchemy import inspect

def init_db():
    """Initialize database tables if they don't exist"""
    try:
        inspector = inspect(engine)
        existing_tables = inspector.get_table_names()
        
        if not existing_tables:
            Base.metadata.create_all(bind=engine)
            print("Database tables created successfully")
        else:
            print("Database tables already exist")
    except Exception as e:
        print(f"ERROR initializing database: {e}")
        raise

if __name__ == "__main__":
    init_db()