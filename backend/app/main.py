from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging
import os

from app.api import router
from app.database import engine
from app.models import Base

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

Base.metadata.create_all(bind=engine)
logger.info("Database tables created")

initialize_db = os.getenv("INITIALIZE_DB", "false").lower() == "true"
logger.info(f"INITIALIZE_DB environment variable: {os.getenv('INITIALIZE_DB', 'Not set')}")
logger.info(f"Will initialize database: {initialize_db}")

if initialize_db:
    logger.info("Starting database initialization process")
    try:
        from app.initialize_db import initialize_database
        initialize_database()
        logger.info("Database initialization completed")
    except ImportError as e:
        logger.error(f"Failed to import initialize_database function: {e}")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}")
else:
    logger.info("Database initialization skipped (not requested)")

app = FastAPI(
    title="Company Registration API",
    description="API for registering and managing companies and their shareholders",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Company Registration API",
        "version": "1.0.0",
        "documentation": "/docs",
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}
