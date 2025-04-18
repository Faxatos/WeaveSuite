import os
from src.db.database import Base, engine
from src.db.models import Microservice, OpenAPISpec, Test, ProxyModification

def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database tables created")

if __name__ == "__main__":
    init_db()