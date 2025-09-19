import json
import logging
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
import re
from datetime import datetime
from typing import List, Dict, Any

import google.generativeai as genai
from sqlalchemy.orm import Session

from db.models import OpenAPISpec, Test, Microservice, Link

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
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-1.5-flash')

    def _extract_microservices_info(self) -> Dict:
        """Extract microservice information including endpoints from database"""
        microservices = self.db.query(Microservice).all()
        
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
            
    def generate_and_store_tests(self) -> Dict[str, Any]:
        """Generate tests from all OpenAPI specs and store them in the database"""
        try:
            #get all specs from the database
            specs = self.db.query(OpenAPISpec).all()
            if not specs:
                logging.warning("No OpenAPI specs found in database")
                return {"status": "error", "message": "No OpenAPI specs found in database"}
            
            #determine if this is the first run (no links exist yet)
            first_run = self.db.query(Link).count() == 0
                
            #microservice infos for the prompt
            microservice_info = self._extract_microservices_info()

            #generate via LLM!
            response_data = self._generate_with_llm(microservice_info, specs, first_run)
            
            tests_created = self._store_tests(response_data.get("tests", ""), specs)
            result = {"status": "success", "tests_created": tests_created}

            if first_run:
                positions_updated = self._store_positions(response_data.get("positions", []))
                links_created = self._store_links(response_data.get("links", []))
                result.update({"positions_updated": positions_updated, "links_created": links_created})

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
    
    def _generate_with_llm(self, microservice_info: Dict, specs: List[OpenAPISpec], include_layout: bool) -> Dict[str, Any]:
        """Generate test code using Google AI API"""
        try:
            #prompt for the LLM
            intro = (
                "You are a QA engineer. Generate pytest tests that hit each endpoint through the API gateway. "
                "Name tests test_<service>_<path>_<method>, include assertions for status codes and response schemas. "
                "IMPORTANT INSTRUCTIONS:\n"
                "1. Analyze the provided microservices data to identify the gateway service (typically named 'gateway')\n"
                "2. Use the gateway's configuration to route requests to the appropriate microservices\n"
                "3. For each microservice endpoint, construct the full URL by combining the gateway base URL with the service path\n"
                "4. All HTTP requests must go through the gateway, never directly to individual services\n"
                "5. Extract authentication requirements from the OpenAPI specs and include proper JWT token handling\n"
                "IMPORTANT: Return ONLY valid JSON in this exact format:\n"
                "{\n"
                ' "tests": "python test code here",\n'
            )
            
            if include_layout: #true only when generating microservices graph
                intro += (
                    '  "positions": [{"name": "service_name", "namespace": "namespace", "x": "x_numeric_position", "y": "y_numeric_position"}],\n'
                    '  "links": [{"source_name": "svc1", "source_namespace": "ns1", "target_name": "svc2", "target_namespace": "ns2", "label": "significant_label"}]\n'
                )
            else:
                intro = intro.rstrip(',\n') + '\n'
            
            intro += "}\n\nDo not include any markdown formatting or explanations, just pure JSON."

            payload = {
                "microservices": microservice_info,
                "openapi_specs": {spec.id: spec.spec for spec in specs}
            }

            #combine system prompt with payload data
            full_prompt = f"{intro}\n\nData: {json.dumps(payload)}"

            #complete prompt being sent to LLM
            logging.info(f"Prompt intro: {intro}")
            logging.info(f"Payload summary:")
            logging.info(f"  - Microservices count: {len(payload['microservices'])}")
            logging.info(f"  - OpenAPI specs count: {len(payload['openapi_specs'])}")
            logging.info(f"  - Include layout: {include_layout}")
            
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
            logging.debug(f"Full prompt content:\n{full_prompt}")

            #generate content using Google AI
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=4000,
                )
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
                        elif key == "positions":
                            if isinstance(value, list):
                                logging.info(f"  - {key}: {len(value)} positions")
                                for pos in value:
                                    if isinstance(pos, dict):
                                        name = pos.get('name', 'Unknown')
                                        namespace = pos.get('namespace', 'Unknown')
                                        x = pos.get('x', 0)
                                        y = pos.get('y', 0)
                                        logging.info(f"      - {name}/{namespace} at ({x}, {y})")
                            else:
                                logging.info(f"  - {key}: {type(value).__name__}")
                        elif key == "links":
                            if isinstance(value, list):
                                logging.info(f"  - {key}: {len(value)} links")
                                for link in value:
                                    if isinstance(link, dict):
                                        source = f"{link.get('source_name', 'Unknown')}/{link.get('source_namespace', 'Unknown')}"
                                        target = f"{link.get('target_name', 'Unknown')}/{link.get('target_namespace', 'Unknown')}"
                                        label = link.get('label', 'No label')
                                        logging.info(f"      - {source} -> {target} ({label})")
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

    def _store_positions(self, positions: List[Dict]) -> int:
        """Update microservice coordinates"""
        logging.info(f"Storing {len(positions)} microservice positions...")
        updated = 0
        for pos in positions:
            ms = self.db.query(Microservice).filter_by(
                name=pos["name"], 
                namespace=pos["namespace"]
            ).first()
            if ms:
                logging.debug(f"Updating position for {pos['name']}/{pos['namespace']}: ({pos.get('x', 0)}, {pos.get('y', 0)})")
                ms.x = pos.get("x", 0.0)
                ms.y = pos.get("y", 0.0)
                updated += 1
            else:
                logging.warning(f"Microservice not found for position update: {pos['name']}/{pos['namespace']}")
        
        self.db.commit()
        logging.info(f"Successfully updated positions for {updated} microservices")
        return updated
    
    def _store_links(self, links: List[Dict]) -> int:
        """Replace existing links with new ones"""
        logging.info(f"Storing {len(links)} microservice links...")
        created = 0
        for link in links:
            source = self._get_microservice(link["source_name"], link["source_namespace"])
            target = self._get_microservice(link["target_name"], link["target_namespace"])
            if source and target:
                logging.debug(f"Creating link: {link['source_name']}/{link['source_namespace']} -> {link['target_name']}/{link['target_namespace']} ({link.get('label', 'No label')})")
                self.db.add(Link(
                    source_id=source.id,
                    target_id=target.id,
                    label=link.get("label", "")
                ))
                created += 1
            else:
                if not source:
                    logging.warning(f"Source microservice not found for link: {link['source_name']}/{link['source_namespace']}")
                if not target:
                    logging.warning(f"Target microservice not found for link: {link['target_name']}/{link['target_namespace']}")
        
        self.db.commit()
        logging.info(f"Successfully created {created} links")
        return created
    
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
        
    def _store_tests(self, test_code: str, specs: List[OpenAPISpec]) -> int:
        """Parse and store individual tests from the generated code"""
        logging.info("Parsing and storing generated test code...")
        logging.info(f"Test code length: {len(test_code)} characters")
        
        #split the test code into individual test functions
        import re
        
        #find all test functions in the code
        test_functions = re.findall(r'def (test_[^\(]+)\([^\)]*\):(.*?)(?=\n\s*def test_|\Z)', 
                                   test_code, re.DOTALL)
        
        logging.info(f"Found {len(test_functions)} test functions in generated code")
        
        tests_created = 0
        
        #store each test function as a separate Test record
        for test_name, test_body in test_functions:
            logging.debug(f"Processing test function: {test_name}")
            
            #try to determine which spec this test is for
            spec_id = None
            for spec in specs:
                spec_title = spec.spec.get('info', {}).get('title', '')
                
                spec_name = spec_title.lower().replace(' ', '_').replace('-', '_')
                if spec_name in test_name:
                    spec_id = spec.id
                    logging.debug(f"  - Matched to spec ID {spec_id} ({spec_title})")
                    break
            
            if not spec_id:
                logging.debug(f"  - No matching spec found for test {test_name}")
            
            #create the complete test function
            complete_test = f"def {test_name}(client):{test_body}"
            
            #extract endpoint path and method info for the test
            endpoint_info = self._extract_endpoint_info(test_name, complete_test)
            logging.debug(f"  - Endpoint: {endpoint_info['method']} ")
            logging.debug(f"  - Path: {endpoint_info['path']}")
            
            #store in the database
            try:
                #check if test already exists
                existing_test = self.db.query(Test).filter_by(name=test_name).first()
                
                if existing_test:
                    #update existing test
                    logging.debug(f"  - Updating existing test: {test_name}")
                    existing_test.code = complete_test
                    existing_test.spec_id = spec_id
                else:
                    #create new test with default values matching the requested format
                    logging.debug(f"  - Creating new test: {test_name}")
                    new_test = Test(
                        name=test_name,
                        code=complete_test,
                        spec_id=spec_id,
                        status="pending",
                        last_execution=None,
                        execution_time=0,
                        error_message=None,
                        services_visited=json.dumps([])  #empty array as JSON string
                    )
                    self.db.add(new_test)
                
                tests_created += 1
                
            except Exception as e:
                logging.error(f"Failed to store test {test_name}: {str(e)}")
                
        try:
            self.db.commit()
            logging.info(f"Successfully stored {tests_created} tests in database")
        except Exception as e:
            self.db.rollback()
            logging.error(f"Failed to commit test changes: {str(e)}")
            raise
            
        return tests_created