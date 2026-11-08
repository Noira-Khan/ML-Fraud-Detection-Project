"""Entry point for the fraud detection pipeline."""

from datetime import datetime, timezone


def run_pipeline() -> None:
    """Run the fraud detection pipeline."""
    started = datetime.now(timezone.utc).isoformat()
    print(f"Fraud detection pipeline started at {started}")


if __name__ == "__main__":
    run_pipeline()
