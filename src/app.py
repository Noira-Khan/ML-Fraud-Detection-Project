"""Run with: uvicorn app:app --app-dir src"""

from fraud_detection_pipeline.api import app

__all__ = ["app"]
