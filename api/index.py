"""Entry point for Vercel's Python (WSGI) runtime. See /vercel.json."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app import app  # noqa: E402
