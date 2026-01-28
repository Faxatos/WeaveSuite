from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Test
from services.discovery_service import DiscoveryService
from services.spec_service import SpecService
from services.generation_service import GenerationService
from services.test_service import TestService
from services.coverage_service import CoverageService, refresh_all_coverage
from scripts.init_db import init_db
import logging

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    #initialize database first
    init_db()
    db = next(get_db())
    try:
        #initial discovery on startup
        DiscoveryService(db).discover_microservices()
        SpecService(db).fetch_and_store_specs()
        
        #generate tests on first execution
        tests_exist = db.query(Test).first() is not None

        #if we have no tests yet
        if not tests_exist:
            GenerationService(db).generate_and_store_tests()
    finally:
        db.close()

@app.get("/api/specs")
async def get_openapi_specs(db: Session = Depends(get_db)):
    """Get all OpenAPI specifications with their microservice details"""
    try:
        specs = DiscoveryService(db).get_openapi_specs()
        
        if not specs:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No OpenAPI specifications available"
            )
        
        return {"specs": specs}
        
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error retrieving OpenAPI specs: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve OpenAPI specs: {str(e)}"
        )

@app.post("/api/update-specs")
async def trigger_update(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manual update trigger endpoint"""
    background_tasks.add_task(
        lambda: DiscoveryService(db).discover_microservices()
    )
    background_tasks.add_task(
        lambda: SpecService(db).fetch_and_store_specs()
    )
    return {"message": "Update process started"}

@app.post("/api/generate-tests")
async def trigger_test_generation(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Generate tests from OpenAPI specs"""
    background_tasks.add_task(
        lambda: GenerationService(db).generate_and_store_tests()
    )
    return {"message": "Test generation process started"}

@app.post("/api/execute-tests")
async def execute_all_tests(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Execute all tests in the database"""
    background_tasks.add_task(
        lambda: TestService(db).execute_all_tests()
    )
    return {"message": "Test execution process started for all tests"}

@app.post("/api/execute-test/{test_id}")
async def execute_single_test(test_id: int, db: Session = Depends(get_db)):
    """Execute a single test by ID"""
    try:
        test_service = TestService(db)
        result = test_service.execute_single_test(test_id)
        
        if result["status"] == "error" and "not found" in result.get("message", "").lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Test with ID {test_id} not found"
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error executing test {test_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to execute test: {str(e)}"
        )

@app.get("/api/system-tests")
async def get_system_tests(db: Session = Depends(get_db)):
    """Get all system tests in the requested format"""
    try:
        tests = GenerationService(db).get_system_tests()
        #check if tests list is empty
        if not tests:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No system tests available"
            )
        return {"tests": tests}
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error retrieving system tests: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve system tests: {str(e)}"
        )
    
@app.post("/api/coverage/refresh")
async def refresh_coverage(db: Session = Depends(get_db)):
    """Full refresh: extract endpoints from specs and analyze all tests"""
    try:
        result = refresh_all_coverage(db)
        return result
    except Exception as e:
        logging.error(f"Error refreshing coverage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to refresh coverage: {str(e)}"
        )

@app.get("/api/coverage/summary")
async def get_coverage_summary(
    spec_id: Optional[int] = Query(None, description="Filter by spec ID"),
    db: Session = Depends(get_db)
):
    """Get coverage summary: total endpoints, covered, uncovered, percentage"""
    try:
        service = CoverageService(db)
        return service.get_coverage_summary(spec_id)
    except Exception as e:
        logging.error(f"Error getting coverage summary: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get coverage summary: {str(e)}"
        )

@app.get("/api/coverage/by-microservice")
async def get_coverage_by_microservice(db: Session = Depends(get_db)):
    """Get coverage breakdown per microservice, sorted by lowest coverage first"""
    try:
        service = CoverageService(db)
        return {"microservices": service.get_coverage_by_microservice()}
    except Exception as e:
        logging.error(f"Error getting coverage by microservice: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get coverage by microservice: {str(e)}"
        )

@app.get("/api/coverage/uncovered")
async def get_uncovered_endpoints(
    spec_id: Optional[int] = Query(None, description="Filter by spec ID"),
    db: Session = Depends(get_db)
):
    """Get list of endpoints not covered by any test"""
    try:
        service = CoverageService(db)
        uncovered = service.get_uncovered_endpoints(spec_id)
        return {
            "count": len(uncovered),
            "endpoints": uncovered
        }
    except Exception as e:
        logging.error(f"Error getting uncovered endpoints: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get uncovered endpoints: {str(e)}"
        )

@app.get("/api/coverage/endpoints")
async def list_endpoints(
    spec_id: Optional[int] = Query(None),
    method: Optional[str] = Query(None),
    covered: Optional[bool] = Query(None),
    db: Session = Depends(get_db)
):
    """List all endpoints with optional filtering"""
    try:
        query = db.query(Endpoint)
        
        if spec_id:
            query = query.filter(Endpoint.spec_id == spec_id)
        if method:
            query = query.filter(Endpoint.method == method.upper())
        
        endpoints = query.all()
        
        # Get covered endpoint IDs
        covered_ids = set(
            row[0] for row in 
            db.query(TestEndpointCoverage.endpoint_id).distinct().all()
        )
        
        result = []
        for ep in endpoints:
            is_covered = ep.id in covered_ids
            
            if covered is not None and is_covered != covered:
                continue
            
            result.append({
                "id": ep.id,
                "spec_id": ep.spec_id,
                "path": ep.path,
                "method": ep.method,
                "operation_id": ep.operation_id,
                "summary": ep.summary,
                "tags": ep.tags,
                "is_covered": is_covered
            })
        
        return {"count": len(result), "endpoints": result}
    except Exception as e:
        logging.error(f"Error listing endpoints: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list endpoints: {str(e)}"
        )

@app.get("/api/coverage/endpoints/{endpoint_id}")
async def get_endpoint_coverage(endpoint_id: int, db: Session = Depends(get_db)):
    """Get which tests cover a specific endpoint"""
    try:
        service = CoverageService(db)
        result = service.get_endpoint_tests(endpoint_id)
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("message")
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting endpoint coverage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get endpoint coverage: {str(e)}"
        )

@app.get("/api/coverage/tests/{test_id}")
async def get_test_coverage(test_id: int, db: Session = Depends(get_db)):
    """Get which endpoints a specific test covers"""
    try:
        service = CoverageService(db)
        result = service.get_test_endpoints(test_id)
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("message")
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error getting test coverage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get test coverage: {str(e)}"
        )

@app.post("/api/coverage/analyze/{test_id}")
async def analyze_single_test(test_id: int, db: Session = Depends(get_db)):
    """Re-analyze a specific test for endpoint coverage"""
    try:
        service = CoverageService(db)
        result = service.analyze_test_coverage(test_id)
        
        if result.get("status") == "error":
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result.get("message")
            )
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error analyzing test coverage: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze test coverage: {str(e)}"
        )

@app.get("/health")
async def health_check():
    return {"status": "healthy"}