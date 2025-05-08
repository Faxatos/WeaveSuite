from kubernetes import client, config
from sqlalchemy.orm import Session
from sqlalchemy import exc
import logging
from src.db.models import Microservice

class DiscoveryService:
    def __init__(self, db: Session):
        self.db = db
        
    def discover_microservices(self):
        """Discover and store new K8s services with proper constraints"""
        try:
            config.load_incluster_config()
            k8s = client.CoreV1Api()
            services = k8s.list_service_for_all_namespaces().items
            
            existing_services = {
                (ms.name, ms.namespace) 
                for ms in self.db.query(Microservice).all()
            }
            
            new_services = []
            
            for service in services:
                name = service.metadata.name
                namespace = service.metadata.namespace
                
                port = service.spec.ports[0].port
                endpoint = f"{name}.{namespace}.svc.cluster.local:{port}"

                if (name, namespace) not in existing_services:
                    try:
                        new_ms = Microservice(
                            name=name,
                            namespace=namespace,
                            endpoint=endpoint
                        )
                        self.db.add(new_ms)
                        new_services.append(name)
                    except exc.IntegrityError:
                        self.db.rollback()
                        logging.warning(f"Duplicate detected: {name}.{namespace}")
            
            self.db.commit()
            return {"discovered": new_services}
            
        except client.exceptions.ApiException as e:  # More specific exception
            logging.error(f"Kubernetes API error: {str(e)}")
            self.db.rollback()
            raise
        except Exception as e:
            logging.error(f"Discovery failed: {str(e)}")
            self.db.rollback()
            raise