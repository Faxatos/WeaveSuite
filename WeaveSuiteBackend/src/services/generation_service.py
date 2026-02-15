import json
import logging
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
import re
from typing import List, Dict, Any

from google import genai
from google.genai import types
from sqlalchemy.orm import Session

from db.models import OpenAPISpec, Test, Microservice, TestTemplate

#logging config
logging.basicConfig(
    level=logging.DEBUG,  # Set to DEBUG to see all logs
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),  # Ensure logs go to stdout
    ]
)

logger = logging.getLogger(__name__)

#load environment variables from the .env file (only useful for debug, when using pods you can set with the manifests env vars)
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

#add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class GenerationService:
    def __init__(self, db: Session):
        self.db = db
        #configure Google AI with API key from env var
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        self.client = genai.Client(api_key=api_key)
        self.model_name = 'gemini-3-pro-preview'

    def _extract_microservices_info(self, valid_ms_ids: List[int]) -> Dict:
        """Extract microservice information including endpoints from database"""
        microservices = self.db.query(Microservice).filter(Microservice.id.in_(valid_ms_ids)).all()
        
        microservice_info = {}
        for ms in microservices:
            microservice_info[str(ms.id)] = {
                "title": ms.name.title() + " Service API",
                "name": ms.name,
                "namespace": ms.namespace,
                "endpoint": ms.endpoint,
                "service_type": ms.service_type,
                "openapi_path": ms.openapi_path
            }
        
        return microservice_info
    
    def _extract_template_from_response(self, test_code: str) -> str:
        """Extract everything before the first test function as template"""
        
        #find the first test function
        first_test_match = re.search(r'\ndef test_', test_code)
        
        if first_test_match:
            #extract everything before the first test function
            template_code = test_code[:first_test_match.start()].strip()
            logging.info(f"Template content:\n{template_code}")
            return template_code
        else:
            logging.warning("No test functions found in response, using empty template")
            return ""
        
    def _store_template(self, template_code: str, template_name: str = "default") -> int:
        """Store or update the extracted template and return template ID"""
        
        if not template_code.strip():
            logging.warning("Empty template code, skipping storage")
            return None
        
        #check if template already exists
        existing_template = self.db.query(TestTemplate).filter_by(name=template_name).first()
        
        if existing_template:
            #check if content is different
            if existing_template.template_code != template_code:
                logging.info(f"Updating existing template '{template_name}'")
                existing_template.template_code = template_code
                template_id = existing_template.id
            else:
                logging.info(f"Template '{template_name}' unchanged, skipping update")
                template_id = existing_template.id
        else:
            #create new template
            logging.info(f"Creating new template '{template_name}'")
            new_template = TestTemplate(
                name=template_name,
                template_code=template_code
            )
            self.db.add(new_template)
            self.db.flush()
            template_id = new_template.id
        
        try:
            self.db.commit()
            logging.info(f"Template '{template_name}' stored successfully with ID {template_id}")
            return template_id
        except Exception as e:
            self.db.rollback()
            logging.error(f"Failed to store template: {str(e)}")
            raise

    def _build_service_config_example(self, microservice_info: Dict) -> str:
        """
        Build a MICROSERVICES dict example from actual microservice data.
        This ensures the LLM uses the correct service names and endpoints.
        Enforces http:// scheme if missing from endpoint.
        """
        lines = []
        for ms_id, ms_data in microservice_info.items():
            service_name = ms_data.get("name", "unknown")
            endpoint = ms_data.get("endpoint", f"http://{service_name}.default.svc.cluster.local:80")
            # Ensure http:// scheme is present — urljoin requires it
            if not endpoint.startswith("http://") and not endpoint.startswith("https://"):
                endpoint = f"http://{endpoint}"
            lines.append(f'    "{service_name}": "{endpoint}",')
        
        return "\n".join(lines) + "\n" if lines else '    # Add service entries here\n'

    def _build_prompt(self, microservice_info: Dict, specs: List[OpenAPISpec]) -> str:
        """
        Build the LLM prompt following Gemini 3 best practices:
        - Direct and concise instructions (no verbose prose)
        - Consistent XML-style tag structure
        - Minimal redundancy (Gemini 3 infers obvious rules)
        - Explicit constraints where ambiguity exists

        Prompt evolution validated via leave-one-out on 3 Kubernetes applications.
        """
        service_config_example = self._build_service_config_example(microservice_info)

        payload = {
            "microservices": microservice_info,
            "openapi_specs": {str(spec.id): spec.spec for spec in specs}
        }

        prompt = (
            "<role>\n"
            "Expert QA Automation Engineer generating production-ready pytest system tests.\n"
            "</role>\n\n"

            "<context>\n"
            "You are given a microservices topology deployed on Kubernetes and their OpenAPI specifications. "
            "Analyze service relationships, endpoints, methods, request/response schemas, and authentication requirements.\n"
            "</context>\n\n"

            "<task>\n"
            "Generate a pytest suite of SYSTEM TESTS that validate the application's end-to-end functionalities "
            "by exercising real workflows across the microservices.\n\n"

            "System test philosophy:\n"
            "- Tests that need existing resources MUST first query the live system to obtain real, valid IDs "
            "(e.g., GET the catalogue to retrieve a real item ID before adding it to a cart, "
            "GET existing users before creating an order). NEVER invent or hardcode resource IDs, names, "
            "or payloads that may not exist in the running system.\n"
            "- For negative/error tests, use clearly invalid data that cannot accidentally match real resources "
            "(e.g., a nonexistent UUID like '00000000-0000-0000-0000-000000000000', empty strings, wrong types, "
            "missing required fields).\n"
            "- When constructing request payloads, include ALL fields defined in the OpenAPI schema for that endpoint. "
            "Cross-reference the schema definition, not just the data available from previous responses.\n"
            "- Think in terms of USER WORKFLOWS and FEATURES, not individual endpoints in isolation.\n"
            "- Each test validates a coherent functional scenario (e.g., browse catalogue then add item to cart, "
            "register user then place order, etc.).\n"
            "- Cover both happy-path AND error scenarios for each key functionality.\n"
            "- Each test MUST be fully independent: create or fetch any prerequisite state at the start of the test. "
            "Do not rely on execution order or shared state between tests.\n"
            "- Always include the response body in assertion messages to aid debugging: "
            "assert resp.status_code == 201, f\"Expected 201, got {resp.status_code}: {resp.text}\"\n"
            "- When a POST/PUT response contains created resource data (IDs, URIs), extract it directly from the response. "
            "Do not make a separate GET call to search for a resource you just created.\n"
            "- When verifying that a resource was created or modified, use the specific endpoint defined in the OpenAPI spec "
            "for that sub-resource. Do not assume nested/embedded data in parent resource responses unless the schema explicitly includes it.\n"
            "- For numeric fields (prices, amounts, quantities), test edge cases and boundary values "
            "(e.g., 0, 1, very small amounts, very large amounts) to uncover undocumented business-rule thresholds. "
            "Happy-path tests should use small, conservative values to avoid hitting unknown limits.\n"
            "- Helper functions that create resources (e.g., register user) must return BOTH the API response data "
            "AND all locally known values (like the username, password, and email used in the request) merged into a single dict, "
            "so tests do not depend on assumptions about the response body shape. "
            "Always include every field from the original request payload in the returned dict.\n"
            "- When parsing API responses, always check the actual type before indexing. If a response could be "
            "a dict (e.g., HAL/JSON:API with _embedded) or a plain list, handle both cases. "
            "Never assume a response is a list and index with [0] without verifying, "
            "and never assume dict keys exist without checking.\n"
            "</task>\n\n"

            "<constraints>\n"
            "- Use ONLY: pytest, requests, Python standard library.\n"
            "- Do NOT use @pytest.mark.parametrize. Write each scenario as a separate test function.\n"
            "- @pytest.fixture is allowed ONLY for shared setup like authentication or session management. "
            "Every fixture parameter in a test function signature must correspond to a defined @pytest.fixture function.\n"
            "- Use the MICROSERVICES dict for all service base URLs (keys = service names from input).\n"
            "- Use get_url(service, path) for ALL URL construction — never hardcode full URLs or use individual variables.\n"
            "- All HTTP calls must include timeout=10.\n"
            "- Naming: test_<service>_<functionality>_<scenario>\n"
            "  Examples: test_catalogue_list_items_happy, test_carts_add_real_item_happy, test_orders_place_with_invalid_id_error\n"
            "- Return ONLY a valid JSON object: { \"tests\": \"<full_python_code>\" }\n"
            "- No markdown, no explanations, no prose outside the JSON.\n"
            "- Ensure proper JSON string escaping: newlines as \\n, quotes as \\\".\n"
            "</constraints>\n\n"

            "<code_template>\n"
            "The generated Python code MUST follow this structure:\n\n"
            "```python\n"
            "import pytest\n"
            "import requests\n"
            "import uuid\n"
            "import random\n"
            "import string\n"
            "from urllib.parse import urljoin\n\n"
            "# --- Service Configuration ---\n"
            "MICROSERVICES = {\n"
            f"{service_config_example}"
            "}\n\n"
            "# --- Helper Functions ---\n"
            "def get_url(service: str, path: str) -> str:\n"
            "    \"\"\"Construct full URL for a service endpoint.\"\"\"\n"
            "    base = MICROSERVICES.get(service)\n"
            "    if not base:\n"
            "        raise ValueError(f\"Service {service} not found in configuration\")\n"
            "    return urljoin(base, path)\n\n"
            "# Add helper functions that query the live system for real data.\n"
            "# Helpers must never return hardcoded or invented data.\n\n"
            "# --- Fixtures ---\n"
            "# Define @pytest.fixture functions for auth tokens, sessions, etc.\n"
            "# Tests that need auth should accept the fixture as a parameter.\n\n"
            "# --- Tests ---\n"
            "# Each test is a standalone function. No @pytest.mark.parametrize.\n"
            "# Fixture parameters are allowed (e.g., def test_orders_create_happy(auth_token):).\n"
            "```\n"
            "</code_template>\n\n"

            "<input>\n"
            f"{json.dumps(payload)}\n"
            "</input>\n"
        )

        return prompt
            
    def generate_and_store_tests(self) -> Dict[str, Any]:
        """Generate tests from all OpenAPI specs and store them in the database"""
        try:
            #get all specs from the database
            specs = self.db.query(OpenAPISpec).all()
            if not specs:
                logging.warning("No OpenAPI specs found in database")
                return {"status": "error", "message": "No OpenAPI specs found in database"}
            
            #microservice infos for the prompt
            ms_ids_with_specs = [spec.microservice_id for spec in specs]
            microservice_info = self._extract_microservices_info(ms_ids_with_specs)

            #generate via LLM!
            response_data = self._generate_with_llm(microservice_info, specs)
            
            #extract and store template from LLM response
            test_code = response_data.get("tests", "")
            template_id = None
            
            if test_code:
                template_code = self._extract_template_from_response(test_code)
                if template_code:
                    template_id = self._store_template(template_code)
            
            tests_created, tests_updated = self._store_tests(test_code, specs, template_id)
            
            result = {
                "status": "success", 
                "tests_created": tests_created, 
                "tests_updated": tests_updated,
                "template_id": template_id
            }

            logging.info(f"Generation completed successfully: {result}")
            return result
            
        except Exception as e:
            logging.error(f"Failed to generate tests: {str(e)}")
            return {"status": "error", "message": f"Failed to generate tests: {str(e)}"}
        
    def get_system_tests(self) -> List[Dict[str, Any]]:
        """Fetch all system tests from the database in the requested format"""
        try:
            tests = self.db.query(Test).all()
            
            result = []
            for test in tests:
                endpoint_info = self._extract_endpoint_info(test.name, test.code)
                
                test_data = {
                    "id": test.id,
                    "name": self._get_friendly_test_name(test.name),
                    "status": test.status or "pending",
                    "code": test.code,
                    "endpoint": endpoint_info,
                    "lastRun": test.last_execution.isoformat() if test.last_execution else None,
                    "duration": test.execution_time,
                    "errorMessage": test.error_message
                }

                result.append(test_data)
            
            return result
            
        except Exception as e:
            logging.error(f"Failed to fetch system tests: {str(e)}")
            return []
    
    def _get_friendly_test_name(self, test_name: str) -> str:
        """Convert test_user_service_get_profile to 'User Profile'"""
        #remove test_ prefix
        if test_name.startswith("test_"):
            name = test_name[5:]
        else:
            name = test_name
            
        #extract meaningful parts and capitalize
        parts = name.split("_")
        #remove method names that might appear at the end
        method_names = ["get", "post", "put", "delete", "patch"]
        filtered_parts = [p for p in parts if p not in method_names and p != "service"]
        
        #join words and capitalize each
        friendly_name = " ".join(word.capitalize() for word in filtered_parts)
        #logging.debug(f"Friendly name result: {friendly_name}")
        return friendly_name
    
    def delete_all_tests(self) -> Dict[str, Any]:
        """Delete all tests and their associated coverage data from the database"""
        try:
            #get count before deletion
            test_count = self.db.query(Test).count()
            
            if test_count == 0:
                logging.info("No tests to delete")
                return {"status": "success", "message": "No tests to delete", "deleted_count": 0}
            
            #delete all tests (cascade will handle TestEndpointCoverage)
            self.db.query(Test).delete()
            self.db.commit()
            
            logging.info(f"Successfully deleted {test_count} tests")
            return {
                "status": "success",
                "message": f"Deleted {test_count} tests",
                "deleted_count": test_count
            }
            
        except Exception as e:
            self.db.rollback()
            logging.error(f"Failed to delete tests: {str(e)}")
            return {"status": "error", "message": f"Failed to delete tests: {str(e)}"}
    
    def _extract_endpoint_info(self, test_name: str, test_code: str) -> Dict[str, Any]:
        """Extract endpoint information from test name and code"""
        endpoint = {
            "path": "",
            "method": "",
            "params": {}
        }
        
        #try to extract method from test name
        method_map = {
            "get": "GET",
            "post": "POST",
            "put": "PUT",
            "delete": "DELETE",
            "patch": "PATCH"
        }
        
        for method_key in method_map:
            if method_key in test_name:
                endpoint["method"] = method_map[method_key]
                break
        
        #extract path and params from code
        if test_code:
            #look for URL patterns in the code
            url_pattern = re.search(r"(client\.(get|post|put|delete|patch)|request\.(get|post|put|delete|patch))\(['\"]([^'\"]+)['\"]", test_code)
            if url_pattern:
                #extract method if we didn't get it from name
                if not endpoint["method"]:
                    method = url_pattern.group(2)
                    endpoint["method"] = method.upper()
                
                #extract path
                path = url_pattern.group(4)
                endpoint["path"] = path
                
                #extract query parameters if present
                if "?" in path:
                    path_part, query_part = path.split("?", 1)  
                    endpoint["path"] = path_part
                    
                    #parse query parameters
                    param_pairs = query_part.split("&")
                    for pair in param_pairs:
                        if "=" in pair:
                            key, value = pair.split("=", 1)
                            endpoint["params"][key] = value
            
            #look for request parameters in the code (for POST/PUT)
            param_pattern = re.search(r"send\(([^)]+)\)", test_code)
            if param_pattern and (endpoint["method"] == "POST" or endpoint["method"] == "PUT"):
                #simplified parameter extraction - in real code would need more robust parsing
                param_body = param_pattern.group(1)
                #add dummy params for demonstration
                if param_body and "{" in param_body:
                    #just identify there are params without parsing the full structure
                    key_pattern = re.findall(r"['\"]([\w]+)['\"]:", param_body)
                    for key in key_pattern:
                        endpoint["params"][key] = "..."
        
        return endpoint
    
    def _generate_with_llm(self, microservice_info: Dict, specs: List[OpenAPISpec]) -> Dict[str, Any]:
        """Generate test code using Google AI API with Gemini 3 optimized prompt"""
        try:
            #build the prompt using the dedicated method
            full_prompt = self._build_prompt(microservice_info, specs)

            #log payload summary
            logging.info("Payload summary:")
            logging.info(f"  - Microservices count: {len(microservice_info)}")
            logging.info(f"  - OpenAPI specs count: {len(specs)}")
            
            #log microservice details
            logging.info("Microservices in payload:")
            for ms_id, ms_info in microservice_info.items():
                logging.info(f"  - ID {ms_id}: {ms_info['name']}/{ms_info['namespace']} ({ms_info['title']})")
            
            #log OpenAPI spec summaries
            logging.info("OpenAPI specs being processed:")
            for spec in specs:
                spec_title = spec.spec.get('info', {}).get('title', 'Unknown')
                spec_version = spec.spec.get('info', {}).get('version', 'Unknown')
                paths_count = len(spec.spec.get('paths', {}))
                logging.info(f"  - Spec ID {spec.id}: '{spec_title}' v{spec_version} ({paths_count} paths)")
                
                for path, methods in spec.spec.get('paths', {}).items():
                    for method in methods.keys():
                        if method.upper() in ['GET', 'POST', 'PUT', 'DELETE', 'PATCH']:
                            logging.info(f"    - {method.upper()} {path}")

            logging.info(f"Full prompt length: {len(full_prompt)} characters")
            logging.info(f"Full prompt:\n{full_prompt}")

            #generate content using Google AI
            config = types.GenerateContentConfig(
                temperature=0.2,
                max_output_tokens=64000,
            )

            response = self.client.models.generate_content(
                model=self.model_name,
                contents=full_prompt,
                config=config
            )

            content = response.text

            logging.info("Response received successfully")
            logging.info(f"Raw response length: {len(content)} characters")
            
            #strip markdown fences if present
            original_content = content
            content = content.strip()
            
            if content.startswith("```json"):
                content = content[len("```json"):].strip()
                if content.endswith("```"):
                    content = content[:-3].strip()
            elif content.startswith("```"):
                #handle generic code fences
                lines = content.split('\n')
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].strip() == "```":
                    lines = lines[:-1]
                content = '\n'.join(lines)
            
            if content != original_content:
                logging.info("Content was modified during fence removal")
                logging.info(f"Processed content length: {len(content)} characters")
                logging.debug(f"Processed content:\n{content}")
            else:
                logging.info("No markdown fences found, content unchanged")
            
            try:
                parsed_response = json.loads(content)
                logging.info("Response structure:")
                
                if isinstance(parsed_response, dict):
                    for key, value in parsed_response.items():
                        if key == "tests":
                            if isinstance(value, str):
                                test_functions = len(re.findall(r'def test_', value))
                                logging.info(f"  - {key}: {test_functions} test functions")
                                
                                test_names = re.findall(r'def (test_[^\(]+)', value)
                                if test_names:
                                    logging.info("    Generated test functions:")
                                    for test_name in test_names:
                                        logging.info(f"      - {test_name}")
                            else:
                                logging.info(f"  - {key}: {type(value).__name__}")
                        else:
                            logging.info(f"  - {key}: {type(value).__name__} - {str(value)[:100]}...")
                else:
                    logging.warning(f"Response is not a dictionary: {type(parsed_response)}")
                
                logging.info("=" * 80)
                return parsed_response
                
            except json.JSONDecodeError as json_err:
                logging.error("JSON parsing failed!")
                logging.error(f"JSON Error: {json_err}")
                logging.error(f"Error position: line {json_err.lineno}, column {json_err.colno}")
                logging.error("Content that failed to parse:")
                logging.error("-" * 40)
                logging.error(content)
                logging.error("-" * 40)
                
                # Try to identify the problematic area
                lines = content.split('\n')
                if hasattr(json_err, 'lineno') and json_err.lineno <= len(lines):
                    problematic_line = lines[json_err.lineno - 1] if json_err.lineno > 0 else "Unknown"
                    logging.error(f"Problematic line {json_err.lineno}: {problematic_line}")
                
                raise Exception(f"Invalid JSON response: {json_err}")
            
        except Exception as e:
            logging.error(f"Error calling Google AI API: {str(e)}")
            logging.error("=" * 80)
            raise
    
    def _get_microservice(self, name: str, namespace: str) -> Microservice:
        ms = self.db.query(Microservice).filter_by(
            name=name, 
            namespace=namespace
        ).first()
        
        if ms:
            logging.debug(f"Found microservice: {name}/{namespace} (ID: {ms.id})")
        else:
            logging.debug(f"Microservice not found: {name}/{namespace}")
            
        return ms
        
    def _store_tests(self, test_code: str, specs: List[OpenAPISpec], template_id: int = None) -> tuple:
        """Parse and store individual tests from the generated code"""
        logging.info("Parsing and storing generated test code...")
        logging.info(f"Test code length: {len(test_code)} characters")
        
        #remove the template part first
        first_test_match = re.search(r'\ndef test_', test_code)
        if first_test_match:
            test_functions_code = test_code[first_test_match.start():].strip()
        else:
            test_functions_code = test_code
        
        #capture the complete function signature including parameters
        test_pattern = r'def (test_[^\(]+)(\([^\)]*\)):(.*?)(?=\ndef test_|\ndef \w+|\Z)'
        test_matches = re.findall(test_pattern, test_functions_code, re.DOTALL)
        
        #clean up function bodies and create complete function definitions
        test_functions = []
        for test_name, test_params, test_body in test_matches:
            #clean the test body (remove leading whitespace, ensure proper indentation)
            lines = test_body.strip().split('\n')
            cleaned_lines = []
            for line in lines:
                if line.strip():
                    #ensure proper indentation (4 spaces)
                    if not line.startswith('    '):
                        cleaned_lines.append('    ' + line.lstrip())
                    else:
                        cleaned_lines.append(line)
                else:
                    cleaned_lines.append('')
            
            #preserve the original parameters when reconstructing the function
            complete_function = f"def {test_name}{test_params}:\n" + '\n'.join(cleaned_lines)
            test_functions.append((test_name, complete_function))
        
        #create a mapping from microservice names to their OpenAPI specs
        microservice_to_specs = {}
        microservices = self.db.query(Microservice).all()
        
        for microservice in microservices:
            service_name = microservice.name.lower()
            microservice_specs = []
            
            #get all specs for this microservice
            for spec in microservice.specs:
                if spec.id in [s.id for s in specs]:
                    microservice_specs.append({
                        'spec_id': spec.id,
                        'microservice_name': microservice.name,
                        'microservice_id': microservice.id,
                        'namespace': microservice.namespace,
                        'spec_title': spec.spec.get('info', {}).get('title', 'Unknown'),
                        'paths': list(spec.spec.get('paths', {}).keys())
                    })
            
            if microservice_specs:
                microservice_to_specs[service_name] = microservice_specs
        
        logging.debug(f"Available microservices: {list(microservice_to_specs.keys())}")
        
        tests_created = 0
        tests_updated = 0
        
        #store each test function as a separate Test record
        for test_name, complete_test in test_functions:
            logging.debug(f"Processing test function: {test_name}")
            
            spec_id = None
            match_reason = None
            
            #extract service name from test name pattern
            test_parts = test_name.split('_')
            
            if len(test_parts) >= 3:
                service_name = test_parts[2].lower()
                
                logging.debug(f"  - Extracted service name: '{service_name}'")
                
                #direct microservice name matching
                if service_name in microservice_to_specs:
                    candidates = microservice_to_specs[service_name]
                    
                    if len(candidates) == 1:
                        spec_id = candidates[0]['spec_id']
                        match_reason = f"microservice '{service_name}' -> spec {spec_id}"
                        logging.debug(f"  - {match_reason}")
                    else:
                        #multiple specs for the same microservice, use the most recent one
                        latest_spec = max(candidates, key=lambda c: c['spec_id'])
                        spec_id = latest_spec['spec_id']
                        match_reason = f"microservice '{service_name}' -> latest spec {spec_id} (out of {len(candidates)} specs)"
                        logging.debug(f"  - {match_reason}")
                else:
                    logging.debug(f"  - No microservice found with name '{service_name}'")
            else:
                logging.debug(f"  - Could not parse service name from test name: {test_name}")
            
            if spec_id:
                logging.debug(f"  - Matched to spec ID {spec_id} ({match_reason})")
            else:
                logging.debug(f"  - No matching spec found for test {test_name}")
            
            try:
                existing_test = self.db.query(Test).filter_by(name=test_name).first()
                if existing_test:
                    logging.debug(f"  - Updating existing test: {test_name}")
                    existing_test.code = complete_test
                    existing_test.spec_id = spec_id
                    existing_test.template_id = template_id
                    existing_test.status = "pending"
                    existing_test.last_execution = None
                    existing_test.execution_time = 0
                    existing_test.error_message = None
                    tests_updated += 1
                else:
                    logging.debug(f"  - Creating new test: {test_name}")
                    new_test = Test(
                        name=test_name,
                        code=complete_test,
                        spec_id=spec_id,
                        template_id=template_id,
                        status="pending",
                        last_execution=None,
                        execution_time=0,
                        error_message=None
                    )
                    self.db.add(new_test)
                    tests_created += 1
            except Exception as e:
                logging.error(f"Failed to store test {test_name}: {str(e)}")
        
        try:
            self.db.commit()
            logging.info(f"Successfully stored {tests_created} new tests / updated {tests_updated} tests in database")
        except Exception as e:
            self.db.rollback()
            logging.error(f"Failed to commit test changes: {str(e)}")
            raise
        
        return tests_created, tests_updated