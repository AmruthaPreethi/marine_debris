import sys
import os

# Make sure the backend root is on the path so `from app.xxx import` works
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app  # noqa: F401 — Vercel picks up `app` from this module
