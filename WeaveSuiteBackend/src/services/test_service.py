import logging
import os
from dotenv import load_dotenv
from pathlib import Path
import sys
import tempfile
import subprocess
from datetime import datetime
from typing import Dict, Any, Optional
import re
import time

from sqlalchemy.orm import Session

from db.models import Test, TestTemplate

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


class TestService:
    def __init__(self, db: Session):
        self.db = db
        self._temp_dir = None

    def _ensure_temp_directory(self) -> str:
        """Create and return the temporary directory path for test execution"""
        if self._temp_dir and os.path.exists(self._temp_dir):
            return self._temp_dir
        
        #in k8s with mounted tmpfs these should work
        preferred_locations = [
            "/tmp",  # Primary tmpfs mount
            "/app/cache",  # Application-specific cache directory
            "/var/run",  # Alternative tmpfs mount
        ]
        
        #try the preferred locations first
        for base_dir in preferred_locations:
            try:
                if not os.path.exists(base_dir):
                    continue
                if not os.access(base_dir, os.W_OK):
                    continue
                    
                temp_dir_name = f"system_tests_{int(time.time())}_{os.getpid()}_temp"
                temp_dir_path = os.path.join(base_dir, temp_dir_name)
                
                os.makedirs(temp_dir_path, mode=0o755, exist_ok=False)
                
                #verify we can write to it
                test_file = os.path.join(temp_dir_path, "test_write")
                with open(test_file, 'w') as f:
                    f.write("test")
                os.unlink(test_file)
                
                self._temp_dir = temp_dir_path
                logging.info(f"Created temporary directory for test execution: {self._temp_dir}")
                return self._temp_dir
                
            except (OSError, PermissionError) as e:
                logging.debug(f"Failed to create temp directory in {base_dir}: {str(e)}")
                continue
        
        #fallback: try standard tempfile.mkdtemp()
        try:
            self._temp_dir = tempfile.mkdtemp(prefix="system_tests_", suffix="_temp")
            os.chmod(self._temp_dir, 0o755)
            logging.info(f"Created temporary directory using tempfile: {self._temp_dir}")
            return self._temp_dir
        except (OSError, PermissionError) as e:
            logging.warning(f"Standard temp directory creation failed: {str(e)}")
        
        error_msg = f"Unable to create temporary directory. Kubernetes tmpfs volumes may not be properly mounted."
        logging.error(error_msg)
        raise Exception(error_msg)

    def _cleanup_temp_directory(self):
        """Clean up the temporary directory and all its contents"""
        if not self._temp_dir:
            return
        
        try:
            if os.path.exists(self._temp_dir):
                import shutil
                # Remove read-only files if any
                def handle_remove_readonly(func, path, exc):
                    os.chmod(path, 0o777)
                    func(path)
                
                shutil.rmtree(self._temp_dir, onerror=handle_remove_readonly)
                logging.info(f"Cleaned up temporary directory: {self._temp_dir}")
            else:
                logging.debug(f"Temporary directory {self._temp_dir} already removed")
                
            self._temp_dir = None
            
        except Exception as e:
            logging.warning(f"Failed to clean up temporary directory {self._temp_dir}: {str(e)}")
            # Don't re-raise the exception as cleanup failures shouldn't stop the main process

    def __del__(self):
        """Cleanup on object destruction"""
        self._cleanup_temp_directory()

    def execute_all_tests(self) -> Dict[str, Any]:
        """Execute all tests in the database"""
        try:
            tests = self.db.query(Test).all()
            if not tests:
                logging.warning("No tests found in database")
                return {"status": "warning", "message": "No tests found in database", "results": []}

            logging.info(f"Found {len(tests)} tests to execute")

            self._ensure_temp_directory()
            
            results = []
            success_count = 0
            failure_count = 0
            error_count = 0

            try:
                for test in tests:
                    result = self.execute_single_test(test.id)
                    results.append(result)
                    
                    if result["status"] == "passed":
                        success_count += 1
                    elif result["status"] == "failed":
                        failure_count += 1
                    else:
                        error_count += 1

                summary = {
                    "status": "success",
                    "total_tests": len(tests),
                    "passed": success_count,
                    "failed": failure_count,
                    "errors": error_count,
                    "results": results
                }

                logging.info(f"Test execution completed: {success_count} passed, {failure_count} failed, {error_count} errors")
                return summary
            
            finally:
                # Clean up temp directory after all tests complete
                self._cleanup_temp_directory()

        except Exception as e:
            logging.error(f"Failed to execute tests: {str(e)}")
            return {"status": "error", "message": f"Failed to execute tests: {str(e)}"}

    def execute_single_test(self, test_id: int) -> Dict[str, Any]:
        """Execute a specific test by ID"""
        try:
            test = self.db.query(Test).filter_by(id=test_id).first()
            if not test:
                logging.error(f"Test with ID {test_id} not found")
                return {"status": "error", "test_id": test_id, "message": "Test not found"}

            logging.info(f"Executing test: {test.name} (ID: {test_id})")

            #combine template and test code
            complete_test_code = self._combine_template_and_test(test)
            if not complete_test_code:
                error_msg = "Failed to combine template and test code"
                logging.error(error_msg)
                self._update_test_results(test, {
                    "status": "error",
                    "error_message": error_msg,
                    "execution_time": 0
                })
                return {"status": "error", "test_id": test_id, "test_name": test.name, "message": error_msg}

            #execute the test
            execution_results = self._execute_pytest_on_code(complete_test_code, test.name)

            #update database with results
            self._update_test_results(test, execution_results)

            result = {
                "status": execution_results["status"],
                "test_id": test_id,
                "test_name": test.name,
                "execution_time": execution_results.get("execution_time", 0),
                "message": execution_results.get("error_message", "")
            }

            if execution_results["status"] == "passed":
                logging.info(f"Test {test.name} PASSED in {execution_results.get('execution_time', 0):.2f}s")
            else:
                logging.warning(f"Test {test.name} {execution_results['status'].upper()}: {execution_results.get('error_message', '')}")

            return result

        except Exception as e:
            logging.error(f"Failed to execute test {test_id}: {str(e)}")
            #try to update the test with error status if possible
            try:
                test = self.db.query(Test).filter_by(id=test_id).first()
                if test:
                    self._update_test_results(test, {
                        "status": "error",
                        "error_message": str(e),
                        "execution_time": 0
                    })
            except:
                pass

            return {"status": "error", "test_id": test_id, "message": str(e)}

    def _combine_template_and_test(self, test: Test) -> Optional[str]:
        """Combine template code with test code to create executable test"""
        try:
            template_code = ""
            
            #get template code if available
            if test.template_id:
                template = self.db.query(TestTemplate).filter_by(id=test.template_id).first()
                if template:
                    template_code = template.template_code
                    logging.debug(f"Using template '{template.name}' for test {test.name}")
                else:
                    logging.warning(f"Template with ID {test.template_id} not found for test {test.name}")
            else:
                logging.info(f"No template specified for test {test.name}")

            #combine template and test code
            if template_code:
                #ensure template code ends with proper spacing
                if not template_code.endswith('\n'):
                    template_code += '\n'
                if not template_code.endswith('\n\n'):
                    template_code += '\n'
                
                combined_code = template_code + test.code
            else:
                #if no template, add minimal imports
                minimal_template = "import pytest\nimport requests\n\n"
                combined_code = minimal_template + test.code

            logging.debug(f"Combined code length: {len(combined_code)} characters")
            logging.debug(f"Combined code preview:\n{combined_code}")

            return combined_code

        except Exception as e:
            logging.error(f"Failed to combine template and test code for {test.name}: {str(e)}")
            return None

    def _execute_pytest_on_code(self, test_code: str, test_name: str) -> Dict[str, Any]:
        """Execute pytest on the combined test code"""
        temp_file_path = None
        try:
            #create temporary file
            temp_file_path = self._create_temp_test_file(test_code, test_name)
            logging.debug(f"Created temporary test file: {temp_file_path}")

            #execute pytest
            cmd = [sys.executable, '-m', 'pytest', temp_file_path, '-v', '--tb=short', '--no-header']
            logging.debug(f"Executing command: {' '.join(cmd)}")

            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300  #5 minute timeout
            )

            #parse pytest output
            results = self._parse_pytest_output(process.stdout, process.stderr, process.returncode)
            
            logging.debug(f"Pytest stdout:\n{process.stdout}")
            if process.stderr:
                logging.debug(f"Pytest stderr:\n{process.stderr}")
            logging.debug(f"Pytest return code: {process.returncode}")

            return results

        except subprocess.TimeoutExpired:
            logging.error(f"Test execution timed out for {test_name}")
            return {
                "status": "error",
                "error_message": "Test execution timed out after 5 minutes",
                "execution_time": 0
            }
        except Exception as e:
            logging.error(f"Failed to execute pytest for {test_name}: {str(e)}")
            return {
                "status": "error",
                "error_message": f"Failed to execute test: {str(e)}",
                "execution_time": 0
            }
        finally:
            #clean up temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.unlink(temp_file_path)
                except Exception as e:
                    logging.warning(f"Failed to clean up temporary file {temp_file_path}: {str(e)}")

    def _create_temp_test_file(self, test_code: str, test_name: str) -> str:
        """Create temporary test file in the dedicated temporary directory"""
        
        #ensure we have a temp directory
        temp_dir = self._ensure_temp_directory()
        
        #generate unique filename
        filename = f"file_{test_name}.py"
        temp_file_path = os.path.join(temp_dir, filename)
        
        try:
            with open(temp_file_path, 'w', encoding='utf-8') as f:
                f.write(test_code)
            
            logging.debug(f"Created temp test file: {temp_file_path}")
            return temp_file_path
            
        except Exception as e:
            raise Exception(f"Unable to create temporary test file: {str(e)}")

    def _extract_error_message(self, stdout: str, stderr: str) -> str:
        """
        Extract a meaningful error message from pytest output.
        
        Priority order:
        1. "E   " lines from the FAILURES section (assertion errors, exceptions)
        2. Collection errors (e.g., "function uses no argument 'prefix'")
        3. "short test summary info" section content
        4. Connection errors from traceback
        5. Special error types (ImportError, SyntaxError, ModuleNotFoundError)
        6. Filtered fallback from last meaningful lines
        """
        combined = stdout + "\n" + stderr
        
        #extract "E   " lines from FAILURES section
        #these contain the actual assertion/exception messages
        failures_match = re.search(
            r'={3,}\s*FAILURES\s*={3,}(.*?)(?:={3,}\s*short test summary|={3,}\s*\d+\s*(?:failed|passed|error))',
            combined,
            re.DOTALL
        )
        if failures_match:
            failures_block = failures_match.group(1)
            
            #extract all "E   " prefixed lines (pytest error lines)
            e_lines = re.findall(r'^\s*E\s+(.+)$', failures_block, re.MULTILINE)
            
            if e_lines:
                #clean up the lines: remove internal pytest decorations
                cleaned_lines = []
                for line in e_lines:
                    line = line.strip()
                    #skip all "+  where" expansion lines - they contain object memory
                    #addresses and internal repr that are noise in error messages.
                    #the actual assertion line already contains the key info.
                    if line.startswith('+') and 'where' in line:
                        continue
                    cleaned_lines.append(line)
                
                if cleaned_lines:
                    error_msg = " | ".join(cleaned_lines)
                    # Simplify connection errors that appear as E lines
                    conn_simplify = re.match(
                        r'requests\.exceptions\.(\w+Error):\s*\w+Pool\(host=[\'"]([^\'"]+)[\'"].*?Caused by \w+\(["\'].*?:\s*(.+?)["\']',
                        error_msg
                    )
                    if conn_simplify:
                        error_msg = f"{conn_simplify.group(1)}: {conn_simplify.group(2)} - {conn_simplify.group(3).rstrip(')')}"
                    return error_msg[:500]
        
        #collection errors
        #e.g., "In test_xxx: function uses no argument 'prefix'"
        #These appear in the ERRORS section, not FAILURES
        errors_match = re.search(
            r'={3,}\s*ERRORS\s*={3,}(.*?)(?:={3,}\s*short test summary|={3,}\s*\d+\s*(?:failed|passed|error))',
            combined,
            re.DOTALL
        )
        if errors_match:
            errors_block = errors_match.group(1)
            #look for collection error messages
            collection_errors = re.findall(r'^\s*E\s+(.+)$', errors_block, re.MULTILINE)
            if collection_errors:
                cleaned = [line.strip() for line in collection_errors 
                          if line.strip() and not re.match(r'^[=\-]{3,}$', line.strip())]
                if cleaned:
                    return " | ".join(cleaned)[:500]
            
            #fallback: look for descriptive lines in error block
            meaningful_lines = []
            for line in errors_block.split('\n'):
                line = line.strip()
                if line and not re.match(r'^[=\-_]{3,}$', line) and not line.startswith('_'):
                    #skip section headers like "___ ERROR collecting ... ___"
                    if not re.match(r'^_+\s.*\s_+$', line):
                        meaningful_lines.append(line)
            if meaningful_lines:
                return " | ".join(meaningful_lines[-3:])[:500]
        
        #short test summary info
        summary_match = re.search(
            r'={3,}\s*short test summary info\s*={3,}\s*\n(.*?)(?:={3,}|\Z)',
            combined,
            re.DOTALL
        )
        if summary_match:
            summary_lines = summary_match.group(1).strip().split('\n')
            #filter out just "FAILED path::test_name" lines with no detail
            detailed_lines = []
            for line in summary_lines:
                line = line.strip()
                if line and not re.match(r'^FAILED\s+\S+::\S+\s*$', line):
                    #has more than just the test path
                    detailed_lines.append(line)
            
            if detailed_lines:
                return " | ".join(detailed_lines)[:500]
        
        #connection errors
        conn_match = re.search(
            r'(requests\.exceptions\.\w+Error:\s*.+?)(?:\n\n|\Z)',
            combined,
            re.DOTALL
        )
        if conn_match:
            error_text = conn_match.group(1).strip()
            #simplify long connection error messages
            #extract just the key info: error type + host + reason
            simple_match = re.match(
                r'(requests\.exceptions\.\w+Error):\s*\w+\(host=[\'"]([^\'"]+)[\'"].*?:\s*(.+?)(?:\)|\Z)',
                error_text,
                re.DOTALL
            )
            if simple_match:
                err_type = simple_match.group(1).split('.')[-1]
                host = simple_match.group(2)
                reason = simple_match.group(3).strip()
                #clean up nested "Caused by" chains
                caused_by = re.search(r'Caused by (\w+Error)\(', reason)
                if caused_by:
                    reason = caused_by.group(1)
                return f"{err_type}: {host} - {reason}"[:500]
            return error_text[:500]
        
        #special error types
        for error_type in ['ImportError', 'SyntaxError', 'ModuleNotFoundError', 'NameError', 'TypeError']:
            type_match = re.search(rf'{error_type}:\s*(.+?)(?:\n|$)', combined)
            if type_match:
                return f"{error_type}: {type_match.group(1).strip()}"[:500]
        
        #pytest.fail() messages
        fail_match = re.search(r'Failed:\s*(.+?)(?:\n|$)', combined)
        if fail_match:
            return f"Failed: {fail_match.group(1).strip()}"[:500]
        
        #fallback - last meaningful lines
        lines = combined.strip().split('\n')
        meaningful = [
            line.strip() for line in lines
            if line.strip() 
            and not re.match(r'^[=\-]{3,}', line.strip())
            and 'FAILED' not in line 
            and 'PASSED' not in line
            and 'collecting' not in line
            and 'test session starts' not in line
            and '::' not in line  # Skip file path lines
        ]
        if meaningful:
            return " | ".join(meaningful[-3:])[:500]
        
        return "Test failed (see logs for details)"

    def _parse_pytest_output(self, stdout: str, stderr: str, return_code: int) -> Dict[str, Any]:
        """Parse pytest output to determine test results"""
        try:
            #default result
            result = {
                "status": "error",
                "error_message": "Unknown error",
                "execution_time": 0
            }

            #extract execution time from pytest output
            execution_time = self._extract_pytest_execution_time(stdout)
            result["execution_time"] = execution_time

            #determine status from return code
            # pytest return codes: 0=all passed, 1=some failed, 2=interrupted/error,
            # 3=internal error, 4=usage error, 5=no tests collected
            if return_code == 0 and "PASSED" in stdout:
                result["status"] = "passed"
                result["error_message"] = None
                return result
            elif return_code == 1:
                #test failures (assertions, exceptions during test)
                result["status"] = "failed"
            elif return_code == 2:
                #interrupted or collection error
                result["status"] = "error"
            elif return_code == 5:
                #no tests collected
                result["status"] = "error"
                result["error_message"] = "No tests were collected - possible collection error"
            else:
                result["status"] = "error"

            #extract meaningful error message for non-passing tests
            if result["status"] != "passed":
                result["error_message"] = self._extract_error_message(stdout, stderr)

            logging.debug(f"Parsed pytest results: {result}")
            return result

        except Exception as e:
            logging.error(f"Failed to parse pytest output: {str(e)}")
            return {
                "status": "error",
                "error_message": f"Failed to parse test results: {str(e)}",
                "execution_time": 0
            }
    
    def _extract_pytest_execution_time(self, stdout: str) -> float:
        """Extract execution time from pytest output"""
        try:
            time_patterns = [
                r'(\d+)\s+(?:passed|failed|error)(?:,\s*\d+\s*(?:passed|failed|error))?\s+in\s+([\d.]+)s',
                r'in\s+([\d.]+)s',
            ]
            
            for i, pattern in enumerate(time_patterns):
                match = re.search(pattern, stdout, re.IGNORECASE)
                if match:
                    try:
                        if i == 0 and len(match.groups()) >= 2:
                            time_str = match.group(2)
                        else:
                            time_str = match.group(1)
                        
                        execution_time = float(time_str)
                        return execution_time
                    except (ValueError, IndexError) as e:
                        logging.debug(f"Failed to extract time from match: {e}")
                        continue
            
            logging.debug("Could not extract execution time from pytest output, defaulting to 0")
            return 0.0
            
        except Exception as e:
            logging.warning(f"Error extracting pytest execution time: {str(e)}")
            return 0.0

    def _update_test_results(self, test: Test, results: Dict[str, Any]):
        """Update test record with execution results"""
        try:
            test.status = results["status"]
            test.last_execution = datetime.utcnow()
            test.execution_time = results.get("execution_time", 0)
            test.error_message = results.get("error_message")

            self.db.commit()

        except Exception as e:
            self.db.rollback()
            logging.error(f"Failed to update test results for {test.name}: {str(e)}")
            raise