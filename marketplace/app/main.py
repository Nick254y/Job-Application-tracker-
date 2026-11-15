from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from pathlib import Path
from app.api.routes import router as api_router
from app.api.auth import router as auth_router
from app.utils.logger import setup_logger
from app.models import init_db
from app.config import settings

BASE_DIR = Path(__file__).resolve().parent
logger = setup_logger(__name__)

# Initialize database at module import time (startup event may not fire in all contexts)
init_db()
logger.info("Database initialized")

app = FastAPI(
    title="DocFlow Marketplace - Payments",
    description="Payment and receipt tracking for property management clients",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")
app.include_router(auth_router, prefix="/api")

app.mount("/static", StaticFiles(directory=BASE_DIR / "templates"), name="static")

@app.get("/")
def root():
    return {"name": "DocFlow Marketplace", "status": "running", "version": "0.1.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    logger.info("Payment system starting up...")
    init_db()
    logger.info("Database initialized")
    logger.info(f"Database URL: {settings.db_url}")
