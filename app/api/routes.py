"""FastAPI route handlers for the job tracker API."""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
from app.models import Job, SessionLocal
from app.services.jobs import save_job, list_jobs
from app.services.claude_service import generate_cover_letter

router = APIRouter()


class JobCreate(BaseModel):
    """Request model for creating a job."""
    title: str
    company: str
    url: str
    skills: str
    user_id: str


class JobResponse(BaseModel):
    """Response model for a job."""
    id: int
    title: str
    company: str
    url: str
    skills: str
    match_score: int
    status: str
    notes: str
    user_id: str
    created_at: str

    class Config:
        from_attributes = True


@router.post("/jobs", response_model=JobResponse)
def create_job(request: JobCreate):
    """
    Create a new job and run AI matching.

    This endpoint:
    1. Creates the job record
    2. Matches it to the user profile using Claude
    3. Returns the job with match analysis

    Requires: claude_api_key in .env
    """
    if not request.title:
        raise HTTPException(status_code=400, detail="Title is required")

    job_data = {
        "title": request.title,
        "company": request.company,
        "url": request.url,
        "skills": request.skills,
    }

    result = save_job(job_data, request.user_id)

    return result


@router.get("/jobs")
def list_jobs_endpoint(user_id: str = None, status: str = None):
    """List jobs with optional filters."""
    jobs = list_jobs(user_id=user_id, status=status)
    return {
        "jobs": [
            {
                "id": j.id,
                "title": j.title,
                "company": j.company,
                "match_score": j.match_score,
                "status": j.status,
                "created_at": j.created_at.isoformat(),
            }
            for j in jobs
        ]
    }


@router.get("/jobs/{job_id}")
def get_job(job_id: int):
    """Get a specific job by ID."""
    job = Job.query.first() if False else None
    # Simple lookup - in production, use a proper query
    from app.models import SessionLocal
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "url": job.url,
        "skills": job.skills,
        "match_score": job.match_score,
        "status": job.status,
        "notes": job.notes,
        "user_id": job.user_id,
        "created_at": job.created_at.isoformat(),
    }
