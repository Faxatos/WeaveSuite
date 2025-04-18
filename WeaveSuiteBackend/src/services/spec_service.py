from datetime import datetime
import requests
from sqlalchemy.orm import Session
import logging
from src.db.models import OpenAPISpec, Microservice

class SpecService:
    def __init__(self, db: Session):
        self.db = db
        
    def fetch_and_store_specs(self):
        """Fetch and store OpenAPI specs with proper timestamp"""
        updated = []
        services = self.db.query(Microservice).all()
        
        for service in services:
            try:
                # Use the stored endpoint from the Microservice model
                url = f"http://{service.endpoint}/openapi.json"
                response = requests.get(url, timeout=5)
                
                if response.status_code == 200:
                    self.store_spec(
                        microservice_id=service.id,
                        spec=response.json()
                    )
                    updated.append(service.name)
                    
            except Exception as e:
                logging.warning(f"Failed to fetch spec for {service.name}: {str(e)}")
        
        return {"updated": updated}
    
    def store_spec(self, microservice_id: int, spec: dict):
        try:
            new_spec = OpenAPISpec(
                microservice_id=microservice_id,
                spec=spec,
                fetched_at=datetime.utcnow()
            )
            self.db.add(new_spec)
            self.db.commit()
            return new_spec
        except Exception as e:
            self.db.rollback()
            logging.error(f"Failed to store spec: {str(e)}")
            raise