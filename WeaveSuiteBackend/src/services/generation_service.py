import json
import logging
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
import re
from datetime import datetime
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
                #extract endpoint info from test name and code
                endpoint_info = self._extract_endpoint_info(test.name, test.code)
                
                #parse services visited from JSON string if available
                services_visited = []
                if test.services_visited:
                    try:
                        services_visited = json.loads(test.services_visited)
                    except json.JSONDecodeError:
                        logging.warning(f"Invalid JSON in services_visited for test {test.id}")
                
                test_data = {
                    "id": test.id,
                    "name": self._get_friendly_test_name(test.name),
                    "status": test.status or "pending",
                    "code": test.code,
                    "endpoint": endpoint_info,
                    "lastRun": test.last_execution.isoformat() if test.last_execution else None,
                    "duration": test.execution_time,
                    "errorMessage": test.error_message,
                    "servicesVisited": services_visited
                }

                #logging.debug(f"test_data: {test_data}")
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
                        endpoint["params"][key] = "..." # Placeholder value
        
        #logging.debug(f"Final endpoint info: {endpoint}")
        return endpoint
    
    def _generate_with_llm(self, microservice_info: Dict, specs: List[OpenAPISpec]) -> Dict[str, Any]:
        """Generate test code using Google AI API"""
        try:
            #prompt for the LLM
            intro = (
                "You are a Expert QA Automation Engineer specializing in Kubernetes-based microservices. Your task is to generate a comprehensive suite of system tests using pytest. "
                "The test code must be complete (no TODOs, no placeholders), self-contained, and executable 'out-of-the-box' without placeholders or manual modifications."
                "Name tests test_<gateway_name>_<service>_<path>_<method>, include meaningfull assertions for status codes and response schemas (assert response structure should matches OpenAPI schemas). "
                "CORE ARCHITECTURAL REQUIREMENTS:\n"
                "1. ROUTING & TOPOLOGY: Analyze the provided microservices data to identify entry points (Gateways) and internal services. "
                "Every test must resolve the correct network path. If a gateway is present, route requests through it using the format: "
                "http://{gateway_endpoint}{routing_prefix}{api_endpoint}. Use absolute URLs inside the test functions.\n"
                "2. NAMING CONVENTION: Name each test function as: test_<entry_point>_<target_service>_<path_slug>_<method>.\n"
                "3. DYNAMIC AUTHENTICATION: Inspect the security schemes in each OpenAPI spec. "
                "If authentication is required (Bearer tokens, API Key, Basic, etc.):\n"
                "   - Create helper functions or pytest fixtures to obtain valid credentials from the appropriate identity endpoint.\n"
                "   - Ensure every test requiring auth explicitly accepts the necessary fixture as a parameter.\n"
                "   - Never hardcode tokens; generate or fetch them dynamically.\n"
                "4. ROBUST ASSERTIONS: Include assertions for HTTP status codes and validate that the response body structure matches the schema defined in the OpenAPI specification.\n"
                "5. DATA INTEGRITY: Use realistic, randomized test data for request bodies and query parameters to ensure unique execution cycles.\n\n"
                
                "TECHNICAL CONSTRAINTS:\n"
                "- Return ONLY a valid JSON object.\n"
                "- Format: { \"tests\": \"<string_containing_full_python_code>\" }\n"
                "- Do not include markdown code blocks (```json), explanations, or prose.\n"
                "- Use only standard Python libraries or common testing libraries like 'requests' or 'pytest'."
            )
            
            
            payload = {
                "microservices": microservice_info,
                "openapi_specs": {spec.id: spec.spec for spec in specs}
            }

            #combine system prompt with payload data
            full_prompt = f"{intro}\n\nData: {json.dumps(payload)}"

            #complete prompt being sent to LLM
            logging.info(f"Payload summary:")
            logging.info(f"  - Microservices count: {len(payload['microservices'])}")
            logging.info(f"  - OpenAPI specs count: {len(payload['openapi_specs'])}")
            
            #log microservice details
            logging.info("Microservices in payload:")
            for spec_id, ms_info in payload['microservices'].items():
                logging.info(f"  - Spec ID {spec_id}: {ms_info['name']}/{ms_info['namespace']} ({ms_info['title']})")
            
            #log OpenAPI spec summaries
            logging.info("OpenAPI specs being processed:")
            for spec_id, spec_data in payload['openapi_specs'].items():
                spec_title = spec_data.get('info', {}).get('title', 'Unknown')
                spec_version = spec_data.get('info', {}).get('version', 'Unknown')
                paths_count = len(spec_data.get('paths', {}))
                logging.info(f"  - Spec ID {spec_id}: '{spec_title}' v{spec_version} ({paths_count} paths)")
                
                for path, methods in spec_data.get('paths', {}).items():
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

            logging.info(f"Response received successfully")
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
                                    logging.info(f"    Generated test functions:")
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
            
            #store in the database
            try:
                #check if test already exists
                existing_test = self.db.query(Test).filter_by(name=test_name).first()
                if existing_test:
                    #update existing test
                    logging.debug(f"  - Updating existing test: {test_name}")
                    existing_test.code = complete_test
                    existing_test.spec_id = spec_id
                    existing_test.template_id = template_id
                    existing_test.status = "pending"
                    existing_test.last_execution = None
                    existing_test.execution_time = 0
                    existing_test.error_message = None
                    existing_test.services_visited = json.dumps([])
                    tests_updated += 1
                else:
                    #create new test
                    logging.debug(f"  - Creating new test: {test_name}")
                    new_test = Test(
                        name=test_name,
                        code=complete_test,
                        spec_id=spec_id,
                        template_id=template_id,
                        status="pending",
                        last_execution=None,
                        execution_time=0,
                        error_message=None,
                        services_visited=json.dumps([])
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