from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
import logging

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