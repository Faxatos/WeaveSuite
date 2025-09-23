from fastapi import FastAPI, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from typing import Dict, Any, List
from sqlalchemy.orm import Session
from db.database import get_db
from db.models import Link
from services.discovery_service import DiscoveryService
from services.spec_service import SpecService
from services.generation_service import GenerationService
from services.test_service import TestService
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
        links = db.query(Link).all()
        if not links:
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

@app.get("/api/graph")
async def get_service_map(db: Session = Depends(get_db)):
    """Get all microservices and their links"""
    try:
        service_map = DiscoveryService(db).get_graph()
        #check if the service map is empty (no nodes or no edges)
        if not service_map.get("nodes") or not service_map.get("edges"):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Service map is empty"
            )
        return service_map
    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Error retrieving service map: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve service map: {str(e)}"
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

@app.get("/health")
async def health_check():
    return {"status": "healthy"}