import re
import ast
import logging
from typing import List, Dict, Any, Optional, Set
from sqlalchemy.orm import Session

from db.models import OpenAPISpec, Endpoint, Test, TestEndpointCoverage, Microservice

logger = logging.getLogger(__name__)


class CoverageService:
    HTTP_METHODS = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options'}
    
    #patterns to detect HTTP calls in test code
    HTTP_CALL_PATTERNS = [
        # requests.get("/path"), requests.post(url), etc.
        r'requests\.(get|post|put|patch|delete|head|options)\s*\(\s*[f]?["\']([^"\']+)["\']',
        r'requests\.(get|post|put|patch|delete|head|options)\s*\(\s*([a-zA-Z_][a-zA-Z0-9_]*)',
        # httpx
        r'httpx\.(get|post|put|patch|delete|head|options)\s*\(\s*[f]?["\']([^"\']+)["\']',
        r'client\.(get|post|put|patch|delete|head|options)\s*\(\s*[f]?["\']([^"\']+)["\']',
        # session.get(), etc.
        r'session\.(get|post|put|patch|delete|head|options)\s*\(\s*[f]?["\']([^"\']+)["\']',
    ]
    
    def __init__(self, db: Session):
        self.db = db
    
    def extract_endpoints_from_spec(self, spec_id: int) -> List[Endpoint]:
        """Extract all endpoints from an OpenAPI spec and store them"""
        spec = self.db.query(OpenAPISpec).filter_by(id=spec_id).first()
        if not spec:
            logger.error(f"OpenAPI spec with ID {spec_id} not found")
            return []
        
        return self._process_openapi_spec(spec)
    
    def extract_all_endpoints(self) -> Dict[str, Any]:
        """Extract endpoints from all OpenAPI specs"""
        specs = self.db.query(OpenAPISpec).all()
        
        total_endpoints = 0
        results = []
        
        for spec in specs:
            endpoints = self._process_openapi_spec(spec)
            total_endpoints += len(endpoints)
            
            ms_name = spec.microservice.name if spec.microservice else "Unknown"
            results.append({
                "spec_id": spec.id,
                "microservice": ms_name,
                "endpoints_count": len(endpoints)
            })
        
        return {
            "status": "success",
            "total_specs": len(specs),
            "total_endpoints": total_endpoints,
            "details": results
        }
    
    def _process_openapi_spec(self, spec: OpenAPISpec) -> List[Endpoint]:
        """Process a single OpenAPI spec and extract/store endpoints"""
        openapi_data = spec.spec
        if not openapi_data:
            return []
        
        paths = openapi_data.get('paths', {})
        endpoints = []
        
        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue
            
            for method in self.HTTP_METHODS:
                if method not in path_item:
                    continue
                
                operation = path_item[method]
                if not isinstance(operation, dict):
                    continue
                
                #check if endpoint already exists
                existing = self.db.query(Endpoint).filter_by(
                    spec_id=spec.id,
                    path=path,
                    method=method.upper()
                ).first()
                
                if existing:
                    existing.operation_id = operation.get('operationId')
                    existing.summary = operation.get('summary')
                    existing.tags = operation.get('tags', [])
                    endpoints.append(existing)
                else:
                    endpoint = Endpoint(
                        spec_id=spec.id,
                        path=path,
                        method=method.upper(),
                        operation_id=operation.get('operationId'),
                        summary=operation.get('summary'),
                        tags=operation.get('tags', [])
                    )
                    self.db.add(endpoint)
                    endpoints.append(endpoint)
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to store endpoints for spec {spec.id}: {e}")
            raise
        
        return endpoints
    
    def analyze_test_coverage(self, test_id: int) -> Dict[str, Any]:
        """Analyze a single test to determine which endpoints it covers"""
        test = self.db.query(Test).filter_by(id=test_id).first()
        if not test:
            return {"status": "error", "message": "Test not found"}
        
        return self._analyze_single_test(test)
    
    def analyze_all_tests(self) -> Dict[str, Any]:
        """Analyze all tests and update coverage mappings"""
        tests = self.db.query(Test).all()
        
        total_mappings = 0
        results = []
        
        for test in tests:
            analysis = self._analyze_single_test(test)
            mappings_count = len(analysis.get("endpoints_matched", []))
            total_mappings += mappings_count
            
            results.append({
                "test_id": test.id,
                "test_name": test.name,
                "endpoints_matched": mappings_count
            })
        
        return {
            "status": "success",
            "total_tests": len(tests),
            "total_mappings": total_mappings,
            "details": results
        }
    
    def _analyze_single_test(self, test: Test) -> Dict[str, Any]:
        """Analyze a single test and create coverage mappings"""
        
        #clear existing coverage for this test
        self.db.query(TestEndpointCoverage).filter_by(test_id=test.id).delete()
        
        #get endpoints to match against
        if test.spec_id:
            endpoints = self.db.query(Endpoint).filter_by(spec_id=test.spec_id).all()
        else:
            endpoints = self.db.query(Endpoint).all()
        
        #extract HTTP calls from test code
        http_calls = self._extract_http_calls(test.code)
        matched_endpoints = []
        
        for method, path in http_calls:
            #find matching endpoint
            endpoint = self._find_matching_endpoint(path, method, endpoints)
            
            if endpoint and endpoint.id not in [e["endpoint_id"] for e in matched_endpoints]:
                #create coverage mapping
                coverage = TestEndpointCoverage(
                    test_id=test.id,
                    endpoint_id=endpoint.id
                )
                self.db.add(coverage)
                
                matched_endpoints.append({
                    "endpoint_id": endpoint.id,
                    "path": endpoint.path,
                    "method": endpoint.method
                })
        
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to store coverage for test {test.id}: {e}")
            return {"status": "error", "message": str(e)}
        
        return {
            "status": "success",
            "test_id": test.id,
            "test_name": test.name,
            "http_calls_found": len(http_calls),
            "endpoints_matched": matched_endpoints
        }
    
    def _extract_http_calls(self, code: str) -> List[tuple]:
        """Extract HTTP method and path from test code"""
        calls = set()
        
        for pattern in self.HTTP_CALL_PATTERNS:
            matches = re.findall(pattern, code, re.IGNORECASE)
            for match in matches:
                method = match[0].upper()
                url_or_path = match[1]
                path = self._extract_path(url_or_path)
                if path:
                    calls.add((method, path))
        
        return list(calls)
    
    def _extract_path(self, url_or_path: str) -> Optional[str]:
        """Extract path from URL or path string"""
        if not url_or_path:
            return None
        
        #if it's already a path
        if url_or_path.startswith('/'):
            return self._normalize_path(url_or_path)
        
        #extract path from full URL
        match = re.search(r'https?://[^/]+(/[^"\'?\s]*)', url_or_path)
        if match:
            return self._normalize_path(match.group(1))
        
        #handle f-string variable parts
        if '{' in url_or_path:
            # Try to extract the path part
            match = re.search(r'(/[a-zA-Z0-9/_\-{}]+)', url_or_path)
            if match:
                return self._normalize_path(match.group(1))
        
        return None
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path: replace IDs with {id}, remove query params"""
        path = path.split('?')[0].rstrip('/')
        
        #replace numeric IDs
        path = re.sub(r'/\d+(?=/|$)', '/{id}', path)
        #replace UUIDs
        path = re.sub(r'/[a-f0-9-]{36}(?=/|$)', '/{id}', path)
        #normalize f-string placeholders
        path = re.sub(r'\{[^}]+\}', '{id}', path)
        
        return path
    
    def _find_matching_endpoint(self, path: str, method: str, endpoints: List[Endpoint]) -> Optional[Endpoint]:
        """Find endpoint matching the given path and method"""
        normalized_path = self._normalize_path(path)
        
        for endpoint in endpoints:
            if endpoint.method != method:
                continue
            
            endpoint_path = self._normalize_path(endpoint.path)
            
            #exact match
            if endpoint_path == normalized_path:
                return endpoint
            
            #pattern match (path parameters)
            pattern = re.sub(r'\{[^}]+\}', r'[^/]+', endpoint_path)
            if re.match(f'^{pattern}$', normalized_path):
                return endpoint
        
        return None
    
    def get_coverage_summary(self, spec_id: Optional[int] = None) -> Dict[str, Any]:
        """Get coverage summary statistics"""
        endpoint_query = self.db.query(Endpoint)
        if spec_id:
            endpoint_query = endpoint_query.filter_by(spec_id=spec_id)
        
        total_endpoints = endpoint_query.count()
        
        #get covered endpoint IDs
        coverage_query = self.db.query(TestEndpointCoverage.endpoint_id).distinct()
        if spec_id:
            coverage_query = coverage_query.join(Endpoint).filter(Endpoint.spec_id == spec_id)
        
        covered_count = coverage_query.count()
        coverage_pct = (covered_count / total_endpoints * 100) if total_endpoints > 0 else 0
        
        return {
            "total_endpoints": total_endpoints,
            "covered_endpoints": covered_count,
            "uncovered_endpoints": total_endpoints - covered_count,
            "coverage_percentage": round(coverage_pct, 2)
        }
    
    def get_coverage_by_microservice(self) -> List[Dict[str, Any]]:
        """Get coverage breakdown by microservice"""
        microservices = self.db.query(Microservice).all()
        results = []
        
        for ms in microservices:
            spec_ids = [spec.id for spec in ms.specs]
            if not spec_ids:
                continue
            
            total = self.db.query(Endpoint).filter(Endpoint.spec_id.in_(spec_ids)).count()
            covered = self.db.query(TestEndpointCoverage.endpoint_id).distinct()\
                .join(Endpoint).filter(Endpoint.spec_id.in_(spec_ids)).count()
            
            coverage_pct = (covered / total * 100) if total > 0 else 0
            
            results.append({
                "microservice_id": ms.id,
                "microservice_name": ms.name,
                "namespace": ms.namespace,
                "total_endpoints": total,
                "covered_endpoints": covered,
                "coverage_percentage": round(coverage_pct, 2)
            })
        
        return sorted(results, key=lambda x: x['coverage_percentage'])
    
    def get_uncovered_endpoints(self, spec_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get list of endpoints not covered by any test"""
        covered_ids = self.db.query(TestEndpointCoverage.endpoint_id).distinct()
        
        query = self.db.query(Endpoint).filter(~Endpoint.id.in_(covered_ids))
        if spec_id:
            query = query.filter_by(spec_id=spec_id)
        
        return [{
            "endpoint_id": ep.id,
            "spec_id": ep.spec_id,
            "path": ep.path,
            "method": ep.method,
            "operation_id": ep.operation_id,
            "summary": ep.summary,
            "tags": ep.tags
        } for ep in query.all()]
    
    def get_endpoint_tests(self, endpoint_id: int) -> Dict[str, Any]:
        """Get tests that cover a specific endpoint"""
        endpoint = self.db.query(Endpoint).filter_by(id=endpoint_id).first()
        if not endpoint:
            return {"status": "error", "message": "Endpoint not found"}
        
        coverages = self.db.query(TestEndpointCoverage).filter_by(endpoint_id=endpoint_id).all()
        
        return {
            "endpoint": {
                "id": endpoint.id,
                "path": endpoint.path,
                "method": endpoint.method,
                "operation_id": endpoint.operation_id
            },
            "is_covered": len(coverages) > 0,
            "tests": [{
                "test_id": cov.test.id,
                "test_name": cov.test.name,
                "test_status": cov.test.status
            } for cov in coverages]
        }
    
    def get_test_endpoints(self, test_id: int) -> Dict[str, Any]:
        """Get endpoints covered by a specific test"""
        test = self.db.query(Test).filter_by(id=test_id).first()
        if not test:
            return {"status": "error", "message": "Test not found"}
        
        coverages = self.db.query(TestEndpointCoverage).filter_by(test_id=test_id).all()
        
        return {
            "test": {
                "id": test.id,
                "name": test.name,
                "status": test.status
            },
            "endpoints": [{
                "endpoint_id": cov.endpoint.id,
                "path": cov.endpoint.path,
                "method": cov.endpoint.method
            } for cov in coverages]
        }


def refresh_all_coverage(db: Session) -> Dict[str, Any]:
    """Full refresh: extract endpoints and analyze all tests"""
    service = CoverageService(db)
    
    extraction = service.extract_all_endpoints()
    analysis = service.analyze_all_tests()
    summary = service.get_coverage_summary()
    
    return {
        "status": "success",
        "extraction": extraction,
        "analysis": analysis,
        "summary": summary
    }