import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any

import openai
from sqlalchemy.orm import Session

from db.models import OpenAPISpec, Test


class TestGenerator:
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
                
            # Combine specs into a single dictionary for the LLM prompt
            combined_specs = {}
            for spec in specs:
                combined_specs[spec.id] = spec.spec
                
            # Generate tests using the LLM
            test_code = self._generate_tests_with_llm(specs, combined_specs)
            
            # Store tests in the database
            tests_created = self._store_tests(test_code, specs)
            
            return {
                "status": "success", 
                "message": f"Generated and stored {tests_created} tests",
                "tests_created": tests_created
            }
            
        except Exception as e:
            logging.error(f"Failed to generate tests: {str(e)}")
            return {"status": "error", "message": f"Failed to generate tests: {str(e)}"}
    
    def _generate_tests_with_llm(self, specs: List[OpenAPISpec], combined_specs: Dict[int, Dict]) -> str:
        """Generate test code using OpenAI API"""
        try:
            # Create a prompt for the LLM
            prompt = (
                "You are a QA engineer. Given these OpenAPI specs, generate a pytest suite\n"
                "that exercises all microservices via 'http://api-gateway'.\n"
                "Name tests as test_<service>_<path>_<method>.\n"
                "Include assertions for status codes and response schemas.\n"
                "Return only executable Python code.\n\n" +
                json.dumps({spec.id: combined_specs[spec.id].get('info', {}).get('title', f'Service_{spec.id}') 
                           for spec in specs}, indent=2) +
                "\n\nHere are the full OpenAPI specs:\n" +
                json.dumps(combined_specs, indent=2)
            )
            
            # Call the OpenAI API
            resp = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.2,
                max_tokens=4000,
            )
            
            # Extract the generated code from the response
            test_code = resp.choices[0].message.content
            
            # Clean up the code (remove markdown code blocks if present)
            if test_code.startswith("```python"):
                test_code = test_code.split("```python")[1]
            if test_code.endswith("```"):
                test_code = test_code.split("```")[0]
                
            test_code = test_code.strip()
            
            logging.info(f"Generated test code with {test_code.count('def test_')} test functions")
            return test_code
            
        except Exception as e:
            logging.error(f"Error calling OpenAI API: {str(e)}")
            raise
    
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
        
    def get_test_coverage_report(self) -> Dict[str, Any]:
        """Generate a report on test coverage across microservices"""
        specs = self.db.query(OpenAPISpec).all()
        tests = self.db.query(Test).all()
        
        coverage = {}
        
        for spec in specs:
            service_name = spec.spec.get('info', {}).get('title', f'Service_{spec.id}')
            paths = spec.spec.get('paths', {})
            total_endpoints = sum(len(methods) for methods in paths.values())
            
            # Count tests associated with this spec
            spec_tests = [test for test in tests if test.spec_id == spec.id]
            
            coverage[service_name] = {
                "total_endpoints": total_endpoints,
                "tests_count": len(spec_tests),
                "coverage_percentage": round(len(spec_tests) / total_endpoints * 100, 2) if total_endpoints else 0
            }
            
        return {
            "overall_services": len(specs),
            "overall_tests": len(tests),
            "service_coverage": coverage
        }