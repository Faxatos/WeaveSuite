from datetime import datetime
import requests
from sqlalchemy.orm import Session
import logging
from urllib.parse import urljoin
from src.db.models import OpenAPISpec, Microservice

class SpecService:
    def __init__(self, db: Session):
        self.db = db
        
    def fetch_and_store_specs(self):
        """Fetch and store OpenAPI specs with proper timestamp"""
        updated = []
        services = self.db.query(Microservice).all()
        
        for service in services:
            spec = None
            for path in ['openapi.json', 'swagger.json']:
                try:
                    #construct URL using urljoin
                    base_url = f"http://{service.endpoint}"
                    full_url = urljoin(base_url, path)
                    response = requests.get(full_url, timeout=5)
                    
                    if response.status_code == 200:
                        spec = response.json()
                        break  # Exit loop on first successful fetch
                except Exception as e:
                    logging.debug(f"Attempt failed for {service.name} at {path}: {str(e)}")
            
            if spec is not None:
                self.store_spec(
                    microservice_id=service.id,
                    spec=spec
                )
                updated.append(service.name)
            else:
                logging.warning(f"Failed to fetch spec for {service.name} from both endpoints")
        
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