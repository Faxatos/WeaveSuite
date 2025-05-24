from kubernetes import client, config
from sqlalchemy.orm import Session
from sqlalchemy import exc
import logging

from typing import Dict, List, Any

from db.models import Microservice, Link

class DiscoveryService:
    def __init__(self, db: Session):
        self.db = db
        
    def discover_microservices(self):
        """Discover and store new K8s services with proper constraints"""
        try:
            config.load_incluster_config()
            k8s = client.CoreV1Api()
            services = k8s.list_service_for_all_namespaces().items
            print(f"Found {len(services)} services in Kubernetes")
            
            existing_services = {
                (ms.name, ms.namespace) 
                for ms in self.db.query(Microservice).all()
            }
            
            new_services = []
            
            for service in services:
                name = service.metadata.name
                namespace = service.metadata.namespace
                labels = service.metadata.labels or {}
                print(f"Processing service {name} in namespace {namespace}")
                print(f"Service labels: {labels}")

                #ToDo: fix logic to understand if the service is a gateway or microservice
                is_gateway = labels.get("gateway", "").lower() == "true"
                service_type = "gateway" if is_gateway else "microservice"
                
                port = service.spec.ports[0].port
                endpoint = f"{name}.{namespace}.svc.cluster.local:{port}"

                if (name, namespace) not in existing_services:
                    try:
                        new_ms = Microservice(
                            name=name,
                            namespace=namespace,
                            endpoint=endpoint,
                            service_type=service_type
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

    def get_graph(self) -> Dict[str, Any]:
        """Get all microservices and their links"""
        try:
            # Fetch all microservices
            microservices = self.db.query(Microservice).all()
            
            # Fetch all links
            links = self.db.query(Link).all()
            
            # Format microservices for the response
            nodes = []
            for ms in microservices:
                node = {
                    "data": {
                        "id": ms.id,
                        "name": ms.name,
                        "namespace": ms.namespace,
                        "endpoint": ms.endpoint,
                        "service_type": ms.service_type
                    },
                    "position": {
                        "x": ms.x,
                        "y": ms.y
                    }
                }
                nodes.append(node)
                
            # Format links for the response
            edges = []
            for link in links:
                edge = {
                    "data": {
                        "id": link.id,
                        "source": link.source_id,
                        "target": link.target_id,
                        "label": link.label or ""
                    }
                }
                edges.append(edge)
                
            print(f"Returning graph with {len(nodes)} nodes and {len(edges)} edges")
            return {
                "nodes": nodes,
                "edges": edges
            }
            
        except Exception as e:
            logging.error(f"Failed to get service map: {str(e)}")
            raise