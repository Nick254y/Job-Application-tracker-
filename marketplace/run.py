#!/usr/bin/env python
"""Run the DocFlow Marketplace payment system."""
from app.main import app
from app.config import settings
from app.models import init_db

if __name__ == "__main__":
    init_db()
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
