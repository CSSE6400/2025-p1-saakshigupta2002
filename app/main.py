from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
import logging
from app.database import Base, engine, SessionLocal
from app.utils.labs import load_labs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create directories if they don't exist
os.makedirs("uploads", exist_ok=True)
os.makedirs("results", exist_ok=True)

# Create the FastAPI application
app = FastAPI(title="CoughOverflow Pathogen Analysis Service")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import models to ensure they are registered with SQLAlchemy
from app.models.analysis import AnalysisJob
from app.models.lab import Lab

# Import routers
from app.api.health import router as health_router
from app.api.labs import router as labs_router
from app.api.patients import router as patients_router
from app.api.analysis import router as analysis_router

# Include routers
app.include_router(health_router, prefix="/api/v1", tags=["Health"])
app.include_router(labs_router, prefix="/api/v1", tags=["Labs"])
app.include_router(patients_router, prefix="/api/v1", tags=["Patients"])
app.include_router(analysis_router, prefix="/api/v1", tags=["Analysis"])

@app.on_event("startup")
async def startup_event():
    logger.info("Starting application initialization")
    try:
        # Create all tables in the database
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
        
        # Load the list of labs
        db = SessionLocal()
        try:
            logger.info("Loading lab data")
            success = load_labs(db)
            if success:
                logger.info("Lab data loaded successfully")
            else:
                logger.warning("Failed to load lab data")
        finally:
            db.close()
            
        logger.info("Application initialization complete")
    except Exception as e:
        logger.error(f"Error during startup: {e}")
        raise