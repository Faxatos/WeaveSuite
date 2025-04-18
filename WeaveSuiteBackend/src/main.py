from fastapi import FastAPI, BackgroundTasks, Depends
from src.db.database import get_db
from src.services.discovery_service import DiscoveryService
from src.services.spec_service import SpecService

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