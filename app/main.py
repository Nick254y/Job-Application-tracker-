"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router as api_router
from app.utils.logger import setup_logger
from app.config import settings

logger = setup_logger(__name__)

app = FastAPI(
    title="Job Tracker Agent",
    description="AI-powered job tracking and matching application",
    version="0.1.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(api_router, prefix="/api")

# Health check endpoint
@app.get("/")
def root():
    """Root endpoint."""
    return {
        "name": "Job Tracker Agent",
        "version": "0.1.0",
        "status": "running",
        "description": "AI-powered job tracking and matching system",
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.on_event("startup")
async def startup_event():
    """Run on application startup."""
    logger.info("Job Tracker Agent starting up...")
    logger.info(f"Database URL: {settings.db_url}")
    logger.info(f"Using model: {settings.anthropic_model}")


@app.on_event("shutdown")
async def shutdown_event():
    """Run on application shutdown."""
    logger.info("Job Tracker Agent shutting down...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
