from datetime import datetime
import requests
from sqlalchemy.orm import Session
import logging
from urllib.parse import urljoin
from db.models import OpenAPISpec, Microservice

class SpecService:
    def __init__(self, db: Session):
        self.db = db
        
    def fetch_and_store_specs(self):
        """Fetch and store OpenAPI specs with proper timestamp"""
        updated = []
        services = self.db.query(Microservice).all()
        
        for service in services:
            logging.info(f"DEBUG: fetching from service: {service.name} (id={service.id}, endpoint={service.endpoint})")
            spec = None

            if service.openapi_path:
                paths_to_try = self._get_paths_from_annotation(service)
            else:
                paths_to_try = self._get_default_paths(service)

            for path in paths_to_try:
                try:
                    base_url = f"http://{service.endpoint}"
                    full_url = urljoin(base_url, path)
                    response = requests.get(full_url, timeout=5)
                    
                    if response.status_code == 200:
                        try:
                            spec_data = response.json()
                            
                            if self._is_valid_openapi_spec(spec_data):
                                spec = spec_data
                                logging.info(f"Successfully fetched spec for {service.name} from {path}")
                                break
                            else:
                                logging.warning(f"Invalid OpenAPI spec for {service.name} at {full_url}")
                                
                        except ValueError as json_error:
                            logging.warning(f"Invalid JSON for {service.name} at {full_url}: {str(json_error)}")
                            
                    else:
                        logging.warning(f"Attempt failed for {service.name} at {full_url}, status code: {response.status_code}")
                        
                except Exception as e:
                    logging.warning(f"Attempt failed for {service.name} at {path}: {str(e)}")
            
            # Store the spec if found
            if spec is not None:
                try:
                    self.store_spec(
                        microservice_id=service.id,
                        spec=spec,
                    )
                    updated.append(service.name)
                    logging.info(f"Stored OpenAPI spec for {service.name} (source: {path})")
                    
                except Exception as store_error:
                    logging.error(f"Failed to store spec for {service.name}: {str(store_error)}")
            else:
                logging.warning(f"Failed to fetch spec for {service.name} from all endpoints, base: {service.endpoint}")
        
        return {"updated": updated}
    
    def _get_paths_from_annotation(self, service):
        """Get OpenAPI paths based on service annotations"""
        paths = []
        
        if service.openapi_path == "gateway-aggregated":
            # Special handling for gateway services
            paths.extend([
                #ToDo: add othet common gateway paths
                'v3/api-docs/swagger-config'
            ])
        elif service.openapi_path:
            # Use the annotated path first
            paths.append(service.openapi_path.lstrip('/'))
            
            # Add some common variations of the annotated path
            annotation_path = service.openapi_path.lstrip('/')
            if not annotation_path.endswith('.json'):
                paths.extend([
                    f"{annotation_path}.json",
                    f"{annotation_path}/swagger.json"
                ])
        
        # Always add fallback paths
        paths.extend(self._get_default_paths(service))
        
        # Remove duplicates while preserving order
        seen = set()
        return [p for p in paths if not (p in seen or seen.add(p))]
    
    def _get_default_paths(self, service):
        """Get default OpenAPI paths to try"""
        default_paths = [
            'api-docs',
            'v3/api-docs',
            'openapi.json', 
            'swagger.json',
            'api/docs', 
            'docs/json', 
            'v1/openapi.json', 
            'v2/openapi.json', 
            'api/v1/openapi.json', 
            'swagger/v1/swagger.json', 
            'swagger-ui/swagger.json'
        ]
        
        # Add gateway-specific paths if this looks like a gateway
        if service.service_type == "gateway" or 'gateway' in service.name.lower():
            gateway_paths = [
                #ToDo: add othet common gateway paths
                'v3/api-docs/swagger-config'
            ]
            return gateway_paths + default_paths
        
        return default_paths
    
    def _is_valid_openapi_spec(self, spec_data):
        """Validate that the fetched data is a valid OpenAPI specification"""
        if not isinstance(spec_data, dict):
            return False
        
        # Check for OpenAPI 3.x
        if 'openapi' in spec_data:
            return True
        
        # Check for Swagger 2.x
        if 'swagger' in spec_data:
            return True
        
        # Check for swagger-config (gateway's config format)
        if 'urls' in spec_data and isinstance(spec_data['urls'], list):
            return True
        
        # Must have basic OpenAPI structure
        return 'info' in spec_data or 'paths' in spec_data
    
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