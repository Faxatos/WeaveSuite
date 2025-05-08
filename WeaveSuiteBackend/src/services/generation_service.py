import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any

import openai
from sqlalchemy.orm import Session

from db.models import OpenAPISpec, Test, Microservice, Link


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

            return result
            
        except Exception as e:
            logging.error(f"Failed to generate tests: {str(e)}")
            return {"status": "error", "message": f"Failed to generate tests: {str(e)}"}
    
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
        return self.db.query(Microservice).filter_by(
            name=name, 
            namespace=namespace
        ).first()
        
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
            
            # Store in the database
            try:
                # Check if test already exists
                existing_test = self.db.query(Test).filter_by(name=test_name).first()
                
                if existing_test:
                    # Update existing test
                    existing_test.code = complete_test
                    existing_test.spec_id = spec_id
                else:
                    # Create new test
                    new_test = Test(
                        name=test_name,
                        code=complete_test,
                        spec_id=spec_id
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