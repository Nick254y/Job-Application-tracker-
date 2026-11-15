"""Job intake and matching service.

This module handles job ingestion from job boards and uses Claude
to match jobs against a user's profile for scoring.
"""

import httpx
from app.config import settings
from app.models import Job, SessionLocal


def save_job(job_data: dict, user_id: str, client=None) -> dict:
    """Save a job to the database and match it to the user profile.

    Args:
        job_data: Dictionary containing job details (title, company, url, skills, etc.)
        user_id: Identifier for the user/job seeker
        client: Optional anthropic.Client instance (for testing)

    Returns:
        dict: Job information with match analysis
    """
    # Create job record
    db = SessionLocal()
    job = Job(
        title=job_data.get("title", ""),
        company=job_data.get("company", ""),
        url=job_data.get("url", ""),
        skills=job_data.get("skills", ""),
        user_id=user_id,
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Match with user profile using Claude
    claude_client = client or anthropic.Anthropic(api_key=settings.claude_api_key)

    match = _match_to_profile(job_data, user_id)

    job.match_score = match.get("match_score", 0)
    job.status = "saved"
    db.commit()

    return {
        "id": job.id,
        "title": job.title,
        "company": job.company,
        "url": job.url,
        "skills": job.skills,
        "match_score": match.get("match_score", 0),
        "suitability": match.get("suitability", "Medium"),
        "key_matches": match.get("key_matches", []),
        "gaps": match.get("gaps", []),
    }


def _match_to_profile(job_data: dict, user_id: str) -> dict:
    """Match job to user profile using Claude API."""
    # Load user profile (this would typically come from a user profile table)
    user_profile = _load_user_profile(user_id)

    message = (
        "A user with these skills and experience is looking for a job:\n"
        f"{user_profile}\n\n"
        "A job posting:\n"
        f"{job_data}\n\n"
        "Analyze the match. Return ONLY a valid JSON object with these fields:\n"
        "  - match_score: integer 0-100\n"
        "  - key_matches: list of strings\n"
        "  - gaps: list of strings\n"
        "  - confidence: integer 0-100\n"
        "  - suitability: 'High', 'Medium', or 'Low'\n"
        "  - suggested_next_action: string"
    )

    try:
        client = anthropic.Anthropic(api_key=settings.claude_api_key)
        response = client.messages.create(
            model=settings.anthropic_model,
            max_tokens=1000,
            messages=[{"role": "user", "content": message}],
        )
        import json
        content = response.content[0].text
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return {
                "match_score": 50,
                "key_matches": [content[:200]],
                "gaps": [],
                "confidence": 50,
                "suitability": "Medium",
                "suggested_next_action": "Review manually",
            }
    except Exception as e:
        return {
            "match_score": 0,
            "key_matches": [],
            "gaps": [str(e)],
            "confidence": 0,
            "suitability": "Low",
            "suggested_next_action": "Manual review required - API error",
        }


def _load_user_profile(user_id: str) -> dict:
    """Load user profile from database or defaults.

    In a production system, this would query the user's profile table.
    For now, returns a default profile based on the user_id.
    """
    # In production, load from user profile table
    # For now, return a default profile
    return {
        "skills": "Python, FastAPI, SQL, JavaScript, React, Git",
        "experience": "Software developer student with 2+ years of experience",
        "education": "Bachelor's in Computer Science",
        "preferred_roles": ["Software Engineer", "Full Stack Developer", "DevOps Engineer"],
        "location": "Remote / Kiambu, Kenya",
    }


def get_job_by_id(job_id: int):
    """Retrieve a job by ID."""
    db = SessionLocal()
    job = db.query(Job).filter(Job.id == job_id).first()
    return job


def list_jobs(user_id: str = None, status: str = None):
    """List jobs with optional filters."""
    db = SessionLocal()
    query = db.query(Job)
    if user_id:
        query = query.filter(Job.user_id == user_id)
    if status:
        query = query.filter(Job.status == status)
    return query.all()
