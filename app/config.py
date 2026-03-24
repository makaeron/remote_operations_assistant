"""Configuration values for the project.

This file keeps the project settings in one place so they are easy to change later.
"""

from pathlib import Path

# Project root folder.
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Local SQLite database file path.
DATABASE_URL = f"sqlite:///{PROJECT_ROOT / 'remote_ops.db'}"

# Folder containing local site runbooks and equipment guidance documents.
RUNBOOKS_DIR = PROJECT_ROOT / "data" / "runbooks"

# How many runbook chunks to return from retrieval.
DEFAULT_TOP_K = 3
