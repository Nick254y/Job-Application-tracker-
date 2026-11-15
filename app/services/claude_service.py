"""Claude API agent services for job analysis and matching.

Uses the Anthropic API to analyze job postings against a user's
profile and extract structured matching data.
"""

import anthropic

from app.config import settings

client = anthropic.Anthropic(api_key=settings.claude_api_key)


def analyze_job_for_matching(job_data: dict, user_profile: dict, model: str = None) -> dict:
    """Analyze a job posting against a user profile using Claude.

    Returns structured matching data including a match score,
    key matches, gaps, and recommended next action.
    """
    if model is None:
        model = settings.anthropic_model

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

    response = client.messages.create(
        model=model,
        max_tokens=1000,
        messages=[{"role": "user", "content": message}],
    )

    content = response.content[0].text

    import json
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        # Fallback: if Claude didn't return valid JSON, try to parse anyway
        return {
            "match_score": 50,
            "key_matches": [content[:200]],
            "gaps": [],
            "confidence": 50,
            "suitability": "Medium",
            "suggested_next_action": "Review manually",
        }


def generate_cover_letter(job_title: str, company: str, skills: str, job_desc: str) -> str:
    """Generate a tailored cover letter for a job application."""
    message = (
        f"Write a professional cover letter for the following job:\n\n"
        f"Job Title: {job_title}\n"
        f"Company: {company}\n"
        f"Required Skills: {skills}\n"
        f"Job Description: {job_desc}\n\n"
        "Write a concise, compelling cover letter (3-4 paragraphs) that highlights "
        "relevant skills and enthusiasm for the role. Use a professional tone."
    )

    response = client.messages.create(
        model=settings.anthropic_model,
        max_tokens=1500,
        messages=[{"role": "user", "content": message}],
    )

    return response.content[0].text
