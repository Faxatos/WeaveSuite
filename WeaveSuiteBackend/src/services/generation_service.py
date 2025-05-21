import json
import logging
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
import re
from datetime import datetime
from typing import List, Dict, Any

import openai
from sqlalchemy.orm import Session

from db.models import OpenAPISpec, Test, Microservice, Link

# Load environment variables from the .env file
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

# Add the parent directory to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class GenerationService:
    def __init__(self, db: Session):
        self.db = db
        # Get API key from environment variable
        openai.api_key = os.getenv("OPENAI_API_KEY")
        if not openai.api_key:
            logging.error("OPENAI_API_KEY environment variable not set")
            raise ValueError("OPENAI_API_KEY environment variable not set")
            
    def generate_and_store_tests(self) -> Dict[str, Any]:
        """Generate tests from all OpenAPI specs and store them in the database"""
        try:
            # Get all specs from the database
            specs = self.db.query(OpenAPISpec).all()
            if not specs:
                logging.warning("No OpenAPI specs found in database")
                return {"status": "error", "message": "No OpenAPI specs found in database"}
            
            # Determine if this is the first run (no links exist yet)
            first_run = self.db.query(Link).count() == 0
                
            # Build microservice info for the prompt
            microservice_info = {
                spec.id: {
                    "title": spec.spec.get("info", {}).get("title", f"Service_{spec.id}"),
                    "name": spec.microservice.name,
                    "namespace": spec.microservice.namespace
                }
                for spec in specs
            }

            # Generate via LLM
            response_data = self._generate_with_llm(microservice_info, specs, first_run)
            
            tests_created = self._store_tests(response_data.get("tests", ""), specs)
            result = {"status": "success", "tests_created": tests_created}

            if first_run:
                positions_updated = self._store_positions(response_data.get("positions", []))
                links_created = self._store_links(response_data.get("links", []))
                result.update({"positions_updated": positions_updated, "links_created": links_created})

            print(f"Store result: {result}")
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
                # Extract endpoint info from test name and code
                endpoint_info = self._extract_endpoint_info(test.name, test.code)
                
                # Parse services visited from JSON string if available
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

                print(f"test_data: {test_data}")
                result.append(test_data)
            
            return result
            
        except Exception as e:
            logging.error(f"Failed to fetch system tests: {str(e)}")
            return []
    
    def _get_friendly_test_name(self, test_name: str) -> str:
        """Convert test_user_service_get_profile to 'User Profile'"""
        # Remove test_ prefix
        if test_name.startswith("test_"):
            name = test_name[5:]
        else:
            name = test_name
            
        # Extract meaningful parts and capitalize
        parts = name.split("_")
        # Remove method names that might appear at the end
        method_names = ["get", "post", "put", "delete", "patch"]
        filtered_parts = [p for p in parts if p not in method_names and p != "service"]
        
        # Join words and capitalize each
        friendly_name = " ".join(word.capitalize() for word in filtered_parts)
        print(f"Friendly name result: {friendly_name}")
        return friendly_name
    
    def _extract_endpoint_info(self, test_name: str, test_code: str) -> Dict[str, Any]:
        """Extract endpoint information from test name and code"""
        endpoint = {
            "path": "",
            "method": "",
            "params": {}
        }
        
        # Try to extract method from test name
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
        
        # Extract path and params from code
        if test_code:
            # Look for URL patterns in the code
            url_pattern = re.search(r"(client\.(get|post|put|delete|patch)|request\.(get|post|put|delete|patch))\(['\"]([^'\"]+)['\"]", test_code)
            if url_pattern:
                # Extract method if we didn't get it from name
                if not endpoint["method"]:
                    method = url_pattern.group(2)
                    endpoint["method"] = method.upper()
                
                # Extract path
                path = url_pattern.group(4)
                endpoint["path"] = path
                
                # Extract query parameters if present
                if "?" in path:
                    path_part, query_part = path.split("?", 1)
                    endpoint["path"] = path_part
                    
                    # Parse query parameters
                    param_pairs = query_part.split("&")
                    for pair in param_pairs:
                        if "=" in pair:
                            key, value = pair.split("=", 1)
                            endpoint["params"][key] = value
            
            # Look for request parameters in the code (for POST/PUT)
            param_pattern = re.search(r"send\(([^)]+)\)", test_code)
            if param_pattern and (endpoint["method"] == "POST" or endpoint["method"] == "PUT"):
                # Simplified parameter extraction - in real code would need more robust parsing
                param_body = param_pattern.group(1)
                # Add dummy params for demonstration
                if param_body and "{" in param_body:
                    # Just identify there are params without parsing the full structure
                    key_pattern = re.findall(r"['\"]([\w]+)['\"]:", param_body)
                    for key in key_pattern:
                        endpoint["params"][key] = "..." # Placeholder value
        
        print(f"Final endpoint info: {endpoint}")
        return endpoint
    
    def _generate_with_llm(self, microservice_info: Dict, specs: List[OpenAPISpec], include_layout: bool) -> Dict[str, Any]:
        """Generate test code using OpenAI API"""
        try:
            # Create a prompt for the LLM
            intro = (
            "You are a QA engineer. Generate pytest tests that hit each endpoint via http://api-gateway. "
            "Name tests test_<service>_<path>_<method>, include assertions for status codes and response schemas."
            )
            if include_layout:
                intro += (
                    " Also provide for each microservices positions (name, namespace, x, y) and directional links "
                    "(source_name, source_namespace, target_name, target_namespace, label) that connects them as a graph."
                )

            payload = {
                "microservices": microservice_info,
                "openapi_specs": {spec.id: spec.spec for spec in specs}
            }

            print(f"Prompt intro: {intro}")
            print(f"Payload keys: {list(payload.keys())}")
            print(f"Microservices in payload: {len(payload['microservices'])}")
            print(f"OpenAPI specs in payload: {len(payload['openapi_specs'])}")

            messages = [
                {"role": "system", "content": intro},
                {"role": "user", "content": json.dumps(payload)}
            ]

            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.2,
                max_tokens=4000,
            )

            content = resp.choices[0].message.content
            # strip markdown fences
            if content.startswith("```json"):
                content = content[len("```json"):].strip().strip('`')
            return json.loads(content)
            
        except Exception as e:
            logging.error(f"Error calling OpenAI API: {str(e)}")
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
        print(f"Updated positions for {updated} microservices")
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
        
        if ms:
            print(f"Found microservice ID: {ms.id}")
        else:
            print(f"Microservice not found: {name}/{namespace}")
            
        return ms
        
    def _store_tests(self, test_code: str, specs: List[OpenAPISpec]) -> int:
        """Parse and store individual tests from the generated code"""
        # Split the test code into individual test functions
        import re
        
        # Find all test functions in the code
        test_functions = re.findall(r'def (test_[^\(]+)\([^\)]*\):(.*?)(?=\n\s*def test_|\Z)', 
                                   test_code, re.DOTALL)
        
        tests_created = 0
        
        # Store each test function as a separate Test record
        for test_name, test_body in test_functions:
            # Try to determine which spec this test is for
            spec_id = None
            for spec in specs:
                spec_title = spec.spec.get('info', {}).get('title', '')
                # Convert to snake case for comparison
                spec_name = spec_title.lower().replace(' ', '_').replace('-', '_')
                if spec_name in test_name:
                    spec_id = spec.id
                    break
            
            # Create the complete test function
            complete_test = f"def {test_name}(client):{test_body}"
            
            # Extract endpoint path and method info for the test
            endpoint_info = self._extract_endpoint_info(test_name, complete_test)
            
            # Store in the database
            try:
                # Check if test already exists
                existing_test = self.db.query(Test).filter_by(name=test_name).first()
                
                if existing_test:
                    # Update existing test
                    existing_test.code = complete_test
                    existing_test.spec_id = spec_id
                else:
                    # Create new test with default values matching the requested format
                    print(f"Creating new test: {test_name}")
                    new_test = Test(
                        name=test_name,
                        code=complete_test,
                        spec_id=spec_id,
                        status="pending",
                        last_execution=None,
                        execution_time=0,
                        error_message=None,
                        services_visited=json.dumps([])  # Empty array as JSON string
                    )
                    self.db.add(new_test)
                
                tests_created += 1
                
            except Exception as e:
                logging.error(f"Failed to store test {test_name}: {str(e)}")
                
        # Commit all changes
        try:
            self.db.commit()
        except Exception as e:
            self.db.rollback()
            logging.error(f"Failed to commit test changes: {str(e)}")
            raise
            
        return tests_created