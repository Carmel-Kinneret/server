import logging
import os
from pathlib import Path

# Load .env if not already loaded elsewhere (the main app loads it)
# We'll still attempt to load LOG_LEVEL from the same .env for safety.
repo_root = Path(__file__).resolve().parents[3]
env_path = repo_root / ".env"
if env_path.is_file():
    from dotenv import load_dotenv
    load_dotenv(env_path)

def get_logger(name: str = "app") -> logging.Logger:
    """Return a configured logger.

    The logger respects the ``LOG_LEVEL`` environment variable (defaults to INFO).
    It uses a concise, timestamped format suitable for both development and
    production logs.
    """
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Ensure we add a handler only once (idempotent)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.propagate = False
    return logger
