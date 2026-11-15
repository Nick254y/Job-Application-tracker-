# Job Tracker Agent

AI-powered job tracking and matching application for helping job seekers find and
apply to jobs. Uses Claude API for intelligent matching and analysis.

## Architecture

- **FastAPI**: Web framework for API endpoints
- **SQLite/PostgreSQL**: Database for storing jobs and applications
- **Anthropic Claude**: AI agent for matching and analysis
- **Queue/Scheduler**: For async job processing (cron, Celery, or hosted)

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your Anthropic API key and settings
   ```

3. **Initialize database:**
   ```bash
   python -c "from app.models import Base; Base.metadata.create_all(bind=engine)"
   ```

4. **Run the application:**
   ```bash
   python run.py
   # or
   uvicorn app.main:app --reload
   ```

5. **Access the API:**
   - API docs: `http://localhost:8000/docs`
   - Health check: `http://localhost:8000/health`

## API Endpoints

- `POST /api/jobs` - Create a job and run AI matching
- `GET /api/jobs` - List jobs (filterable)
- `GET /api/jobs/{id}` - Get a specific job
- `GET /` - Health check

## Workflow

1. Client saves a job posting
2. System extracts job details
3. Claude API analyzes match against user profile
4. Record is stored with match score
5. Alerts are sent on matches (optional)

## Architecture

- **Agent Logic**: Claude API for matching and analysis
- **Queue/Scheduler**: For async job processing
- **Database**: SQLite for local dev, PostgreSQL for production
- **Logging & Alerts**: Email/webhook notifications on events

## Development

### Running Tests

```bash
pip install pytest
pytest tests/
```

### Linting

```bash
pip install flake8
flake8 app tests
```

## Deployment Recommendations

- Run in production with Gunicorn: `gunicorn app.main:app`
- Use a managed database (PostgreSQL) for production
- Set up logging to a centralized logging service
- Configure alerts for critical events
- Use a hosted queue service (Celery, Bull, etc.) for production

## Security Notes

- Never commit .env file to version control
- Use environment variables for all secrets
- Implement rate limiting in production
- Validate all input data
- Use HTTPS in production
