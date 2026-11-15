import logging
import sys
from app.config import settings


def setup_logger(name: str = None, level: str = None):
    """Set up logging with consistent format."""
    if level is None:
        level = settings.log_level

    logger = logging.getLogger(name or __name__)
    logger.setLevel(getattr(logging, level.upper()))

    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(getattr(logging, level.upper()))
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
