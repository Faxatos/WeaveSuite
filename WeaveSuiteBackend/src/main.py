from fastapi import FastAPI, BackgroundTasks, Depends
from src.db.database import get_db
from src.services.discovery_service import DiscoveryService
from src.services.spec_service import SpecService
from src.services.generation_service import GenerationService

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    db = next(get_db())
    try:
        # Initial discovery on startup
        DiscoveryService(db).discover_microservices()
        SpecService(db).fetch_and_store_specs()
    finally:
        db.close()

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

@app.get("/api/system-tests")
async def get_system_tests(db: Session = Depends(get_db)):
    """Get all system tests in the requested format"""
    tests = GenerationService(db).get_system_tests()
    return {"tests": tests}