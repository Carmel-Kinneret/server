import logging
import os
from pathlib import Path

from dotenv import load_dotenv
# Locate and load .env recursively searching up the directory tree
current_dir = Path(__file__).resolve().parent
while current_dir != current_dir.parent:
    env_path = current_dir / ".env"
    if env_path.exists():
        load_dotenv(env_path)
        break
    current_dir = current_dir.parent
else:
    load_dotenv()

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
