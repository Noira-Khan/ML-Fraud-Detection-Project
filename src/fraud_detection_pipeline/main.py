"""Entry point for the fraud detection pipeline."""

from datetime import datetime


def run_pipeline() -> None:
    """Run the fraud detection pipeline."""
    print(f"Fraud detection pipeline started at {datetime.utcnow():isoformat()}Z")


if __name__ == "__main__":
    run_pipeline()
