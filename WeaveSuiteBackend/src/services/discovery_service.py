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
            logging.debug(f"Found {len(services)} services in Kubernetes")
            
            existing_services = {
                (ms.name, ms.namespace) 
                for ms in self.db.query(Microservice).all()
            }
            
            new_services = []
            updated_services = []
            
            for service in services:
                name = service.metadata.name
                namespace = service.metadata.namespace
                labels = service.metadata.labels or {}
                annotations = service.metadata.annotations or {}
                logging.debug(f"Processing service {name} in namespace {namespace}")
                logging.debug(f"Service labels: {labels}")

                openapi_path = self._extract_openapi_path(annotations, labels, name)

                is_gateway = self._is_gateway_service(labels, annotations, name)
                service_type = "gateway" if is_gateway else "microservice"
                
                port = service.spec.ports[0].port if service.spec.ports else 80
                endpoint = f"{name}.{namespace}.svc.cluster.local:{port}"

                service_key = (name, namespace)

                if service_key not in existing_services:
                # Create new microservice
                    try:
                        new_ms = Microservice(
                            name=name,
                            namespace=namespace,
                            endpoint=endpoint,
                            service_type=service_type,
                            openapi_path=openapi_path
                        )
                        self.db.add(new_ms)
                        new_services.append(name)
                        logging.info(f"Added new service: {name} with OpenAPI path: {openapi_path}")
                        
                    except exc.IntegrityError:
                        self.db.rollback()
                        logging.warning(f"Duplicate detected: {name}.{namespace}")
                else:
                    # Update existing microservice if OpenAPI path or other details changed
                    existing_ms = existing_services[service_key]
                    updated = False
                    
                    if existing_ms.openapi_path != openapi_path:
                        existing_ms.openapi_path = openapi_path
                        updated = True
                        
                    if existing_ms.service_type != service_type:
                        existing_ms.service_type = service_type
                        updated = True
                        
                    if existing_ms.endpoint != endpoint:
                        existing_ms.endpoint = endpoint
                        updated = True
                    
                    if updated:
                        updated_services.append(name)
                        logging.info(f"Updated service: {name} with OpenAPI path: {openapi_path}")
            
            self.db.commit()
            return {
                "discovered": new_services,
                "updated": updated_services
            }
            
        except client.exceptions.ApiException as e:
            logging.error(f"Kubernetes API error: {str(e)}")
            self.db.rollback()
            raise
        except Exception as e:
            logging.error(f"Discovery failed: {str(e)}")
            self.db.rollback()
            raise
    
    def _extract_openapi_path(self, annotations, labels, service_name):
        """Extract OpenAPI path from service annotations with fallback logic"""
        
        # Priority order for annotation keys
        annotation_keys = [
            'openapi.io/path',
            'swagger.io/path', 
            'api.io/docs-path',
            'microservice.io/openapi-path',
            'docs.io/openapi-path'
        ]
        
        # Check annotations first
        for key in annotation_keys:
            if key in annotations and annotations[key].strip():
                path = annotations[key].strip()
                logging.info(f"Found OpenAPI path in annotation {key}: {path} for service {service_name}")
                return path
        
        # Check labels as fallback
        for key in annotation_keys:
            label_key = key.replace('/', '-').replace('.', '-')  # Convert to valid label format
            if label_key in labels and labels[label_key].strip():
                path = labels[label_key].strip()
                logging.info(f"Found OpenAPI path in label {label_key}: {path} for service {service_name}")
                return path
        
        # Gateway-specific logic based on service name
        if 'gateway' in service_name.lower():
            return "gateway-aggregated"  # Special marker for gateway services (no annotations here!)
        
        logging.debug(f"No OpenAPI path annotation found for service {service_name}")
        return None
    
    def _is_gateway_service(self, labels, annotations, service_name):
        """Determine if a service is a gateway based on multiple indicators"""
        
        # Check explicit gateway labels/annotations
        gateway_indicators = [
            labels.get("gateway", "").lower() == "true",
            labels.get("app.kubernetes.io/component", "").lower() == "gateway",
            labels.get("service.io/type", "").lower() == "gateway",
            annotations.get("gateway.io/enabled", "").lower() == "true",
            annotations.get("api-gateway.io/enabled", "").lower() == "true"
        ]
        
        if any(gateway_indicators):
            return True
        
        # Check service name patterns
        gateway_name_patterns = ['gateway', 'api-gateway', 'ingress', 'proxy', 'router']
        if any(pattern in service_name.lower() for pattern in gateway_name_patterns):
            return True
        
        return False

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