"""
Coverage Service - Static Endpoint Coverage Analysis

Extracts endpoints from OpenAPI specs, analyzes test code to find HTTP calls,
and maps tests to endpoints to calculate coverage.

Supports both direct HTTP calls and helper function patterns like:
- requests.get("/path")
- get_url("service", "/path") with MICROSERVICES configuration
"""

import re
import logging
from typing import List, Dict, Any, Optional, Tuple
from sqlalchemy.orm import Session

from db.models import OpenAPISpec, Endpoint, Test, TestEndpointCoverage, Microservice, TestTemplate

logger = logging.getLogger(__name__)


class CoverageService:
    """Service for static endpoint coverage analysis"""
    
    HTTP_METHODS = {'get', 'post', 'put', 'patch', 'delete', 'head', 'options'}
    
    # Patterns to detect HTTP calls in test code
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
    
    # Patterns to detect service configuration in templates
    # Handles: MICROSERVICES = {...}, SERVICES = {...}, SERVICE_URLS = {...}
    SERVICE_DICT_PATTERNS = [
        r'MICROSERVICES\s*=\s*\{([^}]+)\}',
        r'SERVICES\s*=\s*\{([^}]+)\}',
        r'SERVICE_URLS\s*=\s*\{([^}]+)\}',
        r'ENDPOINTS\s*=\s*\{([^}]+)\}',
    ]
    
    # Pattern for individual endpoint variables: CARTS_ENDPOINT = "http://..."
    INDIVIDUAL_ENDPOINT_PATTERN = r'([A-Z_]+)_ENDPOINT\s*=\s*["\']([^"\']+)["\']'
    
    # Pattern to detect get_url("service", "/path") helper function usage
    GET_URL_PATTERN = r'get_url\s*\(\s*["\']([^"\']+)["\']\s*,\s*[f]?["\']([^"\']+)["\']\s*\)'
    
    # Pattern for direct URL construction: f"{CARTS_ENDPOINT}/carts"
    DIRECT_URL_PATTERN = r'f?["\']?\{?([A-Z_]+)_ENDPOINT\}?(/[^"\']+)["\']?'
    
    def __init__(self, db: Session):
        self.db = db
        self._microservices_cache: Dict[str, str] = {}
        self._service_to_spec_cache: Dict[str, int] = {}
    
    # ==================== ENDPOINT EXTRACTION ====================
    
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
                
                # Check if endpoint already exists
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
    
    # ==================== TEST ANALYSIS ====================
    
    def analyze_test_coverage(self, test_id: int) -> Dict[str, Any]:
        """Analyze a single test to determine which endpoints it covers"""
        test = self.db.query(Test).filter_by(id=test_id).first()
        if not test:
            return {"status": "error", "message": "Test not found"}
        
        # Build cache if not already built
        if not self._service_to_spec_cache:
            self._build_service_spec_cache()
        
        return self._analyze_single_test(test)
    
    def analyze_all_tests(self) -> Dict[str, Any]:
        """Analyze all tests and update coverage mappings"""
        tests = self.db.query(Test).all()
        
        # Build service-to-spec mapping cache
        self._build_service_spec_cache()
        
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
    
    def _build_service_spec_cache(self):
        """Build a cache mapping service names to spec IDs"""
        self._service_to_spec_cache = {}
        
        microservices = self.db.query(Microservice).all()
        for ms in microservices:
            # Use the microservice name as key (lowercase for matching)
            service_name = ms.name.lower()
            
            # Get the latest spec for this microservice
            if ms.specs:
                latest_spec = max(ms.specs, key=lambda s: s.id)
                self._service_to_spec_cache[service_name] = latest_spec.id
                
                # Also add common variations
                # e.g., "payment-http" -> "payment"
                base_name = service_name.replace('-http', '').replace('-api', '')
                if base_name != service_name:
                    self._service_to_spec_cache[base_name] = latest_spec.id
        
        logger.debug(f"Service-to-spec cache: {self._service_to_spec_cache}")
    
    def _analyze_single_test(self, test: Test) -> Dict[str, Any]:
        """Analyze a single test and create coverage mappings"""
        
        # Clear existing coverage for this test
        self.db.query(TestEndpointCoverage).filter_by(test_id=test.id).delete()
        
        # Get combined code (template + test)
        combined_code = self._get_combined_code(test)
        
        # Parse MICROSERVICES config from template
        microservices_config = self._parse_microservices_config(combined_code)
        
        # Extract HTTP calls from combined code
        http_calls = self._extract_http_calls(combined_code, microservices_config)
        
        # Get all endpoints for matching
        all_endpoints = self.db.query(Endpoint).all()
        
        matched_endpoints = []
        
        for method, path, service_name in http_calls:
            # Determine which spec to match against
            target_spec_id = None
            
            if service_name:
                # Use service name to find the right spec
                target_spec_id = self._service_to_spec_cache.get(service_name.lower())
            elif test.spec_id:
                target_spec_id = test.spec_id
            
            # Filter endpoints by spec if we have a target
            if target_spec_id:
                endpoints = [e for e in all_endpoints if e.spec_id == target_spec_id]
            else:
                endpoints = all_endpoints
            
            # Find matching endpoint
            endpoint = self._find_matching_endpoint(path, method, endpoints)
            
            if endpoint and endpoint.id not in [e["endpoint_id"] for e in matched_endpoints]:
                # Create coverage mapping
                coverage = TestEndpointCoverage(
                    test_id=test.id,
                    endpoint_id=endpoint.id
                )
                self.db.add(coverage)
                
                matched_endpoints.append({
                    "endpoint_id": endpoint.id,
                    "path": endpoint.path,
                    "method": endpoint.method,
                    "service": service_name
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
    
    def _get_combined_code(self, test: Test) -> str:
        """Get combined template + test code for analysis"""
        template_code = ""
        
        if test.template_id:
            template = self.db.query(TestTemplate).filter_by(id=test.template_id).first()
            if template:
                template_code = template.template_code
        
        if template_code:
            return template_code + "\n\n" + test.code
        
        return test.code
    
    def _parse_microservices_config(self, code: str) -> Dict[str, str]:
        """
        Parse service configuration from code to get service -> URL mapping.
        
        Handles multiple patterns:
        - Dict style: MICROSERVICES = {"carts": "http://..."}
        - Dict style: SERVICES = {"carts": "http://..."}
        - Individual: CARTS_ENDPOINT = "http://..."
        """
        config = {}
        
        # Try dict-style patterns first
        for pattern in self.SERVICE_DICT_PATTERNS:
            match = re.search(pattern, code, re.DOTALL)
            if match:
                dict_content = match.group(1)
                
                # Parse key-value pairs like: "carts": "http://carts.sockshop-core.svc.cluster.local:80"
                entries = re.findall(r'["\']([^"\']+)["\']\s*:\s*["\']([^"\']+)["\']', dict_content)
                for service_name, url in entries:
                    config[service_name.lower()] = url
                
                if config:
                    logger.debug(f"Parsed service dict config: {list(config.keys())}")
                    return config
        
        # Try individual endpoint variable pattern
        individual_matches = re.findall(self.INDIVIDUAL_ENDPOINT_PATTERN, code)
        for var_prefix, url in individual_matches:
            # Convert CARTS_ENDPOINT prefix to service name "carts"
            service_name = var_prefix.lower().replace('_', '-')
            # Handle variations like PAYMENT_HTTP -> payment
            service_name = service_name.replace('-http', '').replace('-api', '')
            config[service_name] = url
        
        if config:
            logger.debug(f"Parsed individual endpoint config: {list(config.keys())}")
        
        return config
    
    def _extract_http_calls(self, code: str, microservices_config: Dict[str, str]) -> List[Tuple[str, str, Optional[str]]]:
        """
        Extract HTTP method, path, and service name from test code.
        Returns list of (method, path, service_name) tuples.
        
        Handles multiple patterns:
        - get_url("service", "/path") helper function
        - f"{CARTS_ENDPOINT}/carts/{id}" direct construction
        - requests.get("http://service.../path") direct URLs
        """
        calls = []
        seen = set()
        
        # Pattern 1: Find get_url() calls and their context
        get_url_calls = self._extract_get_url_calls(code, microservices_config)
        for method, path, service_name in get_url_calls:
            key = (method, path, service_name)
            if key not in seen:
                seen.add(key)
                calls.append((method, path, service_name))
        
        # Pattern 2: Find direct endpoint variable usage like f"{CARTS_ENDPOINT}/carts"
        endpoint_var_calls = self._extract_endpoint_var_calls(code, microservices_config)
        for method, path, service_name in endpoint_var_calls:
            key = (method, path, service_name)
            if key not in seen:
                seen.add(key)
                calls.append((method, path, service_name))
        
        # Pattern 3: Find direct HTTP calls with URLs
        for pattern in self.HTTP_CALL_PATTERNS:
            matches = re.findall(pattern, code, re.IGNORECASE)
            for match in matches:
                method = match[0].upper()
                url_or_path = match[1]
                path = self._extract_path(url_or_path)
                
                if path:
                    # Try to determine service from URL
                    service_name = self._extract_service_from_url(url_or_path, microservices_config)
                    key = (method, path, service_name)
                    if key not in seen:
                        seen.add(key)
                        calls.append((method, path, service_name))
        
        return calls
    
    def _extract_endpoint_var_calls(self, code: str, microservices_config: Dict[str, str]) -> List[Tuple[str, str, str]]:
        """
        Extract HTTP calls that use direct endpoint variables like:
        - requests.get(f"{CARTS_ENDPOINT}/carts/{cart_id}")
        - requests.post(ORDERS_ENDPOINT + "/orders", json=...)
        """
        calls = []
        
        # Pattern: requests.method(f"{SERVICE_ENDPOINT}/path" or SERVICE_ENDPOINT + "/path")
        patterns = [
            # f-string: requests.get(f"{CARTS_ENDPOINT}/carts")
            r'requests\.(get|post|put|patch|delete)\s*\(\s*f["\'][^"\']*\{([A-Z_]+_ENDPOINT)\}(/[^"\']*)["\']',
            # Concatenation: requests.get(CARTS_ENDPOINT + "/carts")
            r'requests\.(get|post|put|patch|delete)\s*\(\s*([A-Z_]+_ENDPOINT)\s*\+\s*["\'](/[^"\']+)["\']',
            # Variable then used: url = f"{CARTS_ENDPOINT}/carts" ... requests.get(url)
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, code, re.IGNORECASE)
            for match in matches:
                method = match[0].upper()
                endpoint_var = match[1]
                path = match[2]
                
                # Convert CARTS_ENDPOINT to service name "carts"
                service_name = endpoint_var.replace('_ENDPOINT', '').lower().replace('_', '-')
                service_name = service_name.replace('-http', '').replace('-api', '')
                
                normalized_path = self._normalize_path(path)
                calls.append((method, normalized_path, service_name))
        
        # Also find variable assignments and their usage
        # url = f"{SERVICE_ENDPOINT}/path" ... requests.method(url)
        var_assignments = re.findall(
            r'(\w+)\s*=\s*f["\'][^"\']*\{([A-Z_]+_ENDPOINT)\}(/[^"\']*)["\']',
            code
        )
        
        for var_name, endpoint_var, path in var_assignments:
            # Find how this variable is used
            method_match = re.search(
                rf'requests\.(get|post|put|patch|delete)\s*\(\s*{var_name}[,\)]',
                code, re.IGNORECASE
            )
            if method_match:
                method = method_match.group(1).upper()
                service_name = endpoint_var.replace('_ENDPOINT', '').lower().replace('_', '-')
                service_name = service_name.replace('-http', '').replace('-api', '')
                normalized_path = self._normalize_path(path)
                calls.append((method, normalized_path, service_name))
        
        return calls
    
    def _extract_get_url_calls(self, code: str, microservices_config: Dict[str, str]) -> List[Tuple[str, str, str]]:
        """
        Extract HTTP calls that use get_url("service", "/path") pattern.
        Looks for: url = get_url(...) followed by requests.method(url)
        """
        calls = []
        
        # Find all get_url calls
        get_url_matches = re.findall(self.GET_URL_PATTERN, code)
        
        for service_name, path in get_url_matches:
            # Find the context around this get_url call to determine HTTP method
            method = self._find_http_method_for_get_url(code, service_name, path)
            if method:
                normalized_path = self._normalize_path(path)
                calls.append((method, normalized_path, service_name))
        
        return calls
    
    def _find_http_method_for_get_url(self, code: str, service_name: str, path: str) -> Optional[str]:
        """Find the HTTP method used with a get_url call"""
        escaped_service = re.escape(service_name)
        escaped_path = re.escape(path)
        
        # Pattern 1: Direct assignment followed by requests call
        # url = get_url("service", "/path")
        # response = requests.get(url)
        assignment_pattern = rf'(\w+)\s*=\s*get_url\s*\(\s*["\']{ escaped_service }["\']\s*,\s*[f]?["\']{ escaped_path }["\']\s*\)'
        
        assignment_match = re.search(assignment_pattern, code)
        if assignment_match:
            var_name = assignment_match.group(1)
            # Look for requests.method(var_name
            method_pattern = rf'requests\.(get|post|put|patch|delete|head|options)\s*\(\s*{var_name}[,\)]'
            method_match = re.search(method_pattern, code, re.IGNORECASE)
            if method_match:
                return method_match.group(1).upper()
        
        # Pattern 2: Inline usage
        # response = requests.get(get_url("service", "/path"))
        inline_pattern = rf'requests\.(get|post|put|patch|delete|head|options)\s*\(\s*get_url\s*\(\s*["\']{ escaped_service }["\']\s*,\s*[f]?["\']{ escaped_path }["\']\s*\)'
        inline_match = re.search(inline_pattern, code, re.IGNORECASE)
        if inline_match:
            return inline_match.group(1).upper()
        
        # Pattern 3: Look for any requests call near the get_url (within same function)
        # Find the function containing this get_url
        func_pattern = rf'def\s+(\w+)[^:]*:.*?get_url\s*\(\s*["\']{ escaped_service }["\']\s*,\s*[f]?["\']{ escaped_path }["\']\s*\)'
        func_match = re.search(func_pattern, code, re.DOTALL)
        if func_match:
            func_name = func_match.group(1)
            # Extract the function body
            func_body_pattern = rf'def\s+{func_name}[^:]*:(.*?)(?=\ndef\s|\Z)'
            func_body_match = re.search(func_body_pattern, code, re.DOTALL)
            if func_body_match:
                func_body = func_body_match.group(1)
                # Find requests calls in this function
                method_in_func = re.search(r'requests\.(get|post|put|patch|delete|head|options)\s*\(', func_body, re.IGNORECASE)
                if method_in_func:
                    return method_in_func.group(1).upper()
        
        # Fallback: infer from path patterns
        path_lower = path.lower()
        if '/register' in path_lower or '/login' in path_lower or '/cards' in path_lower or '/addresses' in path_lower:
            return 'POST'
        if '/delete' in path_lower:
            return 'DELETE'
        
        # Default to GET
        return 'GET'
    
    def _extract_service_from_url(self, url: str, microservices_config: Dict[str, str]) -> Optional[str]:
        """Extract service name from URL by matching against MICROSERVICES config"""
        for service_name, base_url in microservices_config.items():
            if base_url in url or service_name in url.lower():
                return service_name
        
        # Try to extract from URL hostname pattern like "carts.sockshop-core.svc"
        match = re.search(r'https?://([a-z0-9-]+)\.', url, re.IGNORECASE)
        if match:
            return match.group(1)
        
        return None
    
    def _extract_path(self, url_or_path: str) -> Optional[str]:
        """Extract path from URL or path string"""
        if not url_or_path:
            return None
        
        # If it's already a path
        if url_or_path.startswith('/'):
            return self._normalize_path(url_or_path)
        
        # Extract path from full URL
        match = re.search(r'https?://[^/]+(/[^"\'?\s]*)', url_or_path)
        if match:
            return self._normalize_path(match.group(1))
        
        # Handle f-string variable parts
        if '{' in url_or_path:
            # Try to extract the path part
            match = re.search(r'(/[a-zA-Z0-9/_\-{}]+)', url_or_path)
            if match:
                return self._normalize_path(match.group(1))
        
        return None
    
    def _normalize_path(self, path: str) -> str:
        """Normalize path: replace IDs with {id}, remove query params"""
        path = path.split('?')[0].rstrip('/')
        
        # Replace numeric IDs
        path = re.sub(r'/\d+(?=/|$)', '/{id}', path)
        # Replace UUIDs
        path = re.sub(r'/[a-f0-9-]{36}(?=/|$)', '/{id}', path)
        # Normalize f-string placeholders like {sock_id}, {user_id}, etc.
        path = re.sub(r'\{[^}]+\}', '{id}', path)
        
        return path
    
    def _find_matching_endpoint(self, path: str, method: str, endpoints: List[Endpoint]) -> Optional[Endpoint]:
        """Find endpoint matching the given path and method"""
        normalized_path = self._normalize_path(path)
        
        for endpoint in endpoints:
            if endpoint.method != method:
                continue
            
            endpoint_path = self._normalize_path(endpoint.path)
            
            # Exact match
            if endpoint_path == normalized_path:
                return endpoint
            
            # Pattern match (path parameters)
            pattern = re.sub(r'\{[^}]+\}', r'[^/]+', endpoint_path)
            if re.match(f'^{pattern}$', normalized_path):
                return endpoint
        
        return None
    
    # ==================== COVERAGE REPORTING ====================
    
    def get_coverage_summary(self, spec_id: Optional[int] = None) -> Dict[str, Any]:
        """Get coverage summary statistics"""
        endpoint_query = self.db.query(Endpoint)
        if spec_id:
            endpoint_query = endpoint_query.filter_by(spec_id=spec_id)
        
        total_endpoints = endpoint_query.count()
        
        # Get covered endpoint IDs
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