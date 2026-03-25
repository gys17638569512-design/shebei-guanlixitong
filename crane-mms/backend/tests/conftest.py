from __future__ import annotations

import os
from pathlib import Path


TEST_DB_PATH = Path(__file__).resolve().parent / ".pytest-bootstrap.db"


# Provide the minimum required settings before application modules import.
os.environ.setdefault("DATABASE_URL", f"sqlite:///{TEST_DB_PATH}")
os.environ.setdefault("SECRET_KEY", "pytest-secret-key")
