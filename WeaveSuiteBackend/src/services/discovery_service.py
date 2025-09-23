from kubernetes import client, config
from sqlalchemy.orm import Session
from sqlalchemy import exc
import logging

from typing import Dict, List, Any

from db.models import Microservice, Link

class DiscoveryService:
    def __init__(self, db: Session):
        self.db = db
        
        #define excluded namespaces (system namespaces)
        self.excluded_namespaces = {
            'kube-system',
            'ingress-nginx',
            'kube-public',
            'kube-node-lease',
            'kubernetes-dashboard'
        }
        
        #define excluded service names (infrastructure services)
        self.excluded_services = {
            'kubernetes',
            'kube-dns',
            'metrics-server',
            'postgres', #ToDo: name weavesuite postgres as weavesuite-postgres
            'weavesuite-backend',
            'weavesuite-frontend',
        }
        
        #define excluded service patterns
        self.excluded_patterns = [
            'weavesuite', #future proof!
            'admission',
            'controller'
        ]
        
    def discover_microservices(self):
        """Discover and store new K8s services with proper constraints and architecture filtering"""
        try:
            config.load_incluster_config()
            k8s = client.CoreV1Api()
            services = k8s.list_service_for_all_namespaces().items
            #logging.debug(f"Found {len(services)} services in Kubernetes")
            
            existing_services = {
                (ms.name, ms.namespace): ms 
                for ms in self.db.query(Microservice).all()
            }
            
            new_services = []
            updated_services = []
            excluded_count = 0
            
            for service in services:
                name = service.metadata.name
                namespace = service.metadata.namespace
                labels = service.metadata.labels or {}
                annotations = service.metadata.annotations or {}
                
                #check if service should be excluded
                if self._should_exclude_service(name, namespace, labels, annotations):
                    excluded_count += 1
                    continue
                
                #logging.debug(f"Processing service {name} in namespace {namespace}")
                #logging.debug(f"Service labels: {labels}")

                openapi_path = self._extract_openapi_path(annotations, labels, name)

                is_gateway = self._is_gateway_service(labels, annotations, name)
                service_type = "gateway" if is_gateway else "microservice"
                
                port = service.spec.ports[0].port if service.spec.ports else 80
                endpoint = f"{name}.{namespace}.svc.cluster.local:{port}"

                service_key = (name, namespace)

                if service_key not in existing_services:
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
                        #logging.info(f"Added new service: {name} with OpenAPI path: {openapi_path}")
                        
                    except exc.IntegrityError:
                        self.db.rollback()
                        #logging.warning(f"Duplicate detected: {name}.{namespace}")
                else:
                    #update existing microservice if OpenAPI path or other details changed
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
                        #logging.info(f"Updated service: {name} with OpenAPI path: {openapi_path}")
            
            self.db.commit()
            logging.info(f"Discovery complete: {len(new_services)} new, {len(updated_services)} updated, {excluded_count} excluded")
            
            return {
                "discovered": new_services,
                "updated": updated_services,
                "excluded": excluded_count
            }
            
        except client.exceptions.ApiException as e:
            logging.error(f"Kubernetes API error: {str(e)}")
            self.db.rollback()
            raise
        except Exception as e:
            logging.error(f"Discovery failed: {str(e)}")
            self.db.rollback()
            raise

    def _should_exclude_service(self, name: str, namespace: str, labels: dict, annotations: dict) -> bool:
        """Determine if a service should be excluded from discovery"""
        
        #exclude services from system namespaces
        if namespace in self.excluded_namespaces:
            #logging.debug(f"Excluding service {name} from system namespace {namespace}")
            return True
        
        #exclude specific infrastructure services
        if name in self.excluded_services:
            #logging.debug(f"Excluding infrastructure service {name}")
            return True
        
        #exclude services matching certain patterns
        name_lower = name.lower()
        for pattern in self.excluded_patterns:
            if pattern in name_lower:
                #logging.debug(f"Excluding service {name} matching pattern '{pattern}'")
                return True
        
        #exclude services with specific labels indicating they're not part of the business architecture
        infrastructure_labels = [
            labels.get("app.kubernetes.io/component") in ["controller", "admission", "dns", "metrics"],
            labels.get("k8s-app") in ["kube-dns", "metrics-server"],
            labels.get("app") in ["postgres", "database", "zipkin"],
            labels.get("component") in ["database", "monitoring", "logging"]
        ]
        
        if any(infrastructure_labels):
            #logging.debug(f"Excluding service {name} based on infrastructure labels")
            return True
        
        #exclude services with monitoring/logging annotations
        monitoring_annotations = [
            "prometheus.io/scrape" in annotations,
            "logging.coreos.com/" in str(annotations.keys()),
            "monitoring.coreos.com/" in str(annotations.keys())
        ]
        
        #only exclude if it's clearly a monitoring service (not just being monitored)
        if any(monitoring_annotations) and any(monitor_name in name_lower for monitor_name in ['prometheus', 'grafana', 'jaeger', 'zipkin']):
            #logging.debug(f"Excluding monitoring service {name}")
            return True
        
        return False
    
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
        
        #check annotations first
        for key in annotation_keys:
            if key in annotations and annotations[key].strip():
                path = annotations[key].strip()
                #logging.info(f"Found OpenAPI path in annotation {key}: {path} for service {service_name}")
                return path
        
        #check labels as fallback
        for key in annotation_keys:
            label_key = key.replace('/', '-').replace('.', '-')  # Convert to valid label format
            if label_key in labels and labels[label_key].strip():
                path = labels[label_key].strip()
                #logging.info(f"Found OpenAPI path in label {label_key}: {path} for service {service_name}")
                return path
        
        #gateway-specific logic based on service name
        if 'gateway' in service_name.lower():
            return "gateway-aggregated"
        
        #logging.debug(f"No OpenAPI path annotation found for service {service_name}")
        return None
    
    def _is_gateway_service(self, labels, annotations, service_name):
        """Determine if a service is a gateway based on multiple indicators"""
        
        #check explicit gateway labels/annotations
        gateway_indicators = [
            labels.get("gateway", "").lower() == "true",
            labels.get("app.kubernetes.io/component", "").lower() == "gateway",
            labels.get("service.io/type", "").lower() == "gateway",
            annotations.get("gateway.io/enabled", "").lower() == "true",
            annotations.get("api-gateway.io/enabled", "").lower() == "true"
        ]
        
        if any(gateway_indicators):
            return True
        
        #check service name patterns (but exclude ingress controllers which are infrastructure)
        gateway_name_patterns = ['gateway', 'api-gateway']
        if any(pattern in service_name.lower() for pattern in gateway_name_patterns):
            #make sure it's not an infrastructure gateway like ingress controller
            if 'ingress' not in service_name.lower() and 'controller' not in service_name.lower():
                return True
        
        return False

    def get_graph(self) -> Dict[str, Any]:
        """Get all microservices and their links"""
        try:
            microservices = self.db.query(Microservice).all()
            links = self.db.query(Link).all()
            
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

    def get_openapi_specs(self):
        """Get all OpenAPI specifications with their microservice details"""
        try:
            from db.models import OpenAPISpec, Microservice
            
            specs_query = self.db.query(OpenAPISpec).join(Microservice).all()
            
            if not specs_query:
                return []
            
            specs_data = []
            for spec in specs_query:
                spec_status = "available"
                try:
                    if not spec.spec or not isinstance(spec.spec, dict):
                        spec_status = "error"
                    elif "openapi" not in spec.spec and "swagger" not in spec.spec:
                        spec_status = "error"
                    elif not spec.spec.get("paths"):
                        spec_status = "unavailable"
                except Exception:
                    spec_status = "error"
                
                spec_data = {
                    "id": spec.id,
                    "spec": spec.spec,
                    "fetched_at": spec.fetched_at.isoformat() if spec.fetched_at else None,
                    "microservice_id": spec.microservice_id,
                    "microservice": {
                        "id": spec.microservice.id,
                        "name": spec.microservice.name,
                        "url": spec.microservice.url,
                        "version": getattr(spec.microservice, 'version', None)
                    },
                    "status": spec_status
                }
                specs_data.append(spec_data)
            
            return specs_data
            
        except Exception as e:
            logging.error(f"Error retrieving OpenAPI specs: {str(e)}")
            raise Exception(f"Failed to retrieve OpenAPI specs: {str(e)}")