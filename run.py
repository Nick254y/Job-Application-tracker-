#!/usr/bin/env python
"""Run the Job Tracker Agent application."""

from app.main import app
from app.config import settings

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=settings.log_level == "DEBUG",
    )
