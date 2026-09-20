"""Refuse to run database tests against a developer or production database."""

import os
from urllib.parse import urlparse


database = urlparse(os.environ.get("DATABASE_URL", ""))
if os.environ.get("TESTING", "").lower() != "true" or not database.path.endswith("_test"):
    raise RuntimeError(
        "Set TESTING=true and DATABASE_URL to a dedicated *_test database before pytest."
    )
