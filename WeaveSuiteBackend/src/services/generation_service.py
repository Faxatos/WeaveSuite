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
                
            #build microservice info for the prompt
            microservice_info = {
                spec.id: {
                    "title": spec.spec.get("info", {}).get("title", f"Service_{spec.id}"),
                    "name": spec.microservice.name,
                    "namespace": spec.microservice.namespace
                }
                for spec in specs
            }

            #generate via LLM!
            response_data = self._generate_with_llm(microservice_info, specs, first_run)
            
            tests_created = self._store_tests(response_data.get("tests", ""), specs)
            result = {"status": "success", "tests_created": tests_created}

            if first_run:
                positions_updated = self._store_positions(response_data.get("positions", []))
                links_created = self._store_links(response_data.get("links", []))
                result.update({"positions_updated": positions_updated, "links_created": links_created})

            #logging.debug(f"Store result: {result}")
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
                "You are a QA engineer. Generate pytest tests that hit each endpoint via http://api-gateway. "
                "Name tests test_<service>_<path>_<method>, include assertions for status codes and response schemas. "
                "The tests must be performed ALWAYS from the gateway endpoint, that you can find in microservices payload, taking 'endpoint' of 'service_type' = gateway. "
                "IMPORTANT: Return ONLY valid JSON in this exact format:\n"
                "{\n"
                '  "tests": "python test code here",\n'
            )
            
            if include_layout:
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

            logging.info(f"Prompt intro: {intro}")
            logging.info(f"Payload keys: {list(payload.keys())}")
            logging.debug(f"Microservices in payload: {len(payload['microservices'])}")
            logging.debug(f"OpenAPI specs in payload: {len(payload['openapi_specs'])}")

            #combine system prompt with payload data
            full_prompt = f"{intro}\n\nData: {json.dumps(payload)}"

            #generate content using Google AI
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.2,
                    max_output_tokens=4000,
                )
            )

            #check if response is valid
            if not response or not hasattr(response, 'text'):
                logging.error("No response received from Google AI API")
                raise Exception("No response received from Google AI API")
            
            content = response.text
            if not content:
                logging.error("Empty response from Google AI API")
                raise Exception("Empty response from Google AI API")
            
            #logging.debug(f"Raw response content: {content[:500]}...") 
            
            #strip markdown fences if present
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
            
            #validate that we have content before parsing
            if not content.strip():
                logging.error("Content is empty after processing")
                raise Exception("Content is empty after processing")
            
            try:
                return json.loads(content)
            except json.JSONDecodeError as json_err:
                logging.error(f"Failed to parse JSON. Content: {content}")
                raise Exception(f"Invalid JSON response: {json_err}")
            
        except Exception as e:
            logging.error(f"Error calling Google AI API: {str(e)}")
            raise

    def _store_positions(self, positions: List[Dict]) -> int:
        """Update microservice coordinates"""
        updated = 0
        for pos in positions:
            ms = self.db.query(Microservice).filter_by(
                name=pos["name"], 
                namespace=pos["namespace"]
            ).first()
            if ms:
                ms.x = pos.get("x", 0.0)
                ms.y = pos.get("y", 0.0)
                updated += 1
        self.db.commit()
        #logging.debug(f"Updated positions for {updated} microservices")
        return updated
    
    def _store_links(self, links: List[Dict]) -> int:
        """Replace existing links with new ones"""
        #self.db.query(Link).delete()  # Clear old links
        created = 0
        for link in links:
            source = self._get_microservice(link["source_name"], link["source_namespace"])
            target = self._get_microservice(link["target_name"], link["target_namespace"])
            if source and target:
                self.db.add(Link(
                    source_id=source.id,
                    target_id=target.id,
                    label=link.get("label", "")
                ))
                created += 1
        self.db.commit()
        return created
    
    def _get_microservice(self, name: str, namespace: str) -> Microservice:
        ms = self.db.query(Microservice).filter_by(
            name=name, 
            namespace=namespace
        ).first()
        
        #if ms:
        #    logging.info(f"Found microservice ID: {ms.id}")
        #else:
        #    logging.info(f"Microservice not found: {name}/{namespace}")
            
        return ms
        
    def _store_tests(self, test_code: str, specs: List[OpenAPISpec]) -> int:
        """Parse and store individual tests from the generated code"""
        #split the test code into individual test functions
        import re
        
        #find all test functions in the code
        test_functions = re.findall(r'def (test_[^\(]+)\([^\)]*\):(.*?)(?=\n\s*def test_|\Z)', 
                                   test_code, re.DOTALL)
        
        tests_created = 0
        
        #store each test function as a separate Test record
        for test_name, test_body in test_functions:
            #try to determine which spec this test is for
            spec_id = None
            for spec in specs:
                spec_title = spec.spec.get('info', {}).get('title', '')
                
                spec_name = spec_title.lower().replace(' ', '_').replace('-', '_')
                if spec_name in test_name:
                    spec_id = spec.id
                    break
            
            #create the complete test function
            complete_test = f"def {test_name}(client):{test_body}"
            
            #extract endpoint path and method info for the test
            endpoint_info = self._extract_endpoint_info(test_name, complete_test)
            
            #store in the database
            try:
                #check if test already exists
                existing_test = self.db.query(Test).filter_by(name=test_name).first()
                
                if existing_test:
                    #update existing test
                    existing_test.code = complete_test
                    existing_test.spec_id = spec_id
                else:
                    #create new test with default values matching the requested format
                    logging.debug(f"Creating new test: {test_name}")
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
        except Exception as e:
            self.db.rollback()
            logging.error(f"Failed to commit test changes: {str(e)}")
            raise
            
        return tests_created