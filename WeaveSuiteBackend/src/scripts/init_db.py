from src.db.database import Base, engine

def init_db():
    try:
        Base.metadata.create_all(bind=engine)  
        print("Database tables created successfully")
    except Exception as e:
        print(f"ERROR creating database tables: {e}")
        raise

if __name__ == "__main__":
    init_db()