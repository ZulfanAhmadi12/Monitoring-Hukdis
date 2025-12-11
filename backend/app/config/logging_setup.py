import logging
import os
from .settings import settings

# =============================
# Directory & File Setup
# =============================
LOG_DIR = os.path.join(settings.BASE_DIR, "logs")
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, "backend_error.log")

# =============================
# Root Logger Configuration
# =============================
logger = logging.getLogger()
logger.setLevel(logging.INFO)   # console receives INFO+

# Remove any existing handlers to prevent duplicates
for h in logger.handlers[:]:
    logger.removeHandler(h)

# =============================
# Console Handler → INFO, WARNING, ERROR
# =============================
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))

# =============================
# File Handler → WARNING + ERROR only
# =============================
file_handler = logging.FileHandler(LOG_FILE, encoding="utf-8")
file_handler.setLevel(logging.WARNING)
file_handler.setFormatter(logging.Formatter(
    "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
))

# =============================
# Register handlers
# =============================
logger.addHandler(console_handler)
logger.addHandler(file_handler)

