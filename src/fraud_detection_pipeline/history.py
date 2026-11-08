"""Local log of payments scored in this demo.

The file lives on this computer and is not a bank ledger. It is gitignored.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

import pandas as pd

from fraud_detection_pipeline.scoring import PROJECT_ROOT

COLUMNS = [
    "scored_at",
    "source",
    "amount",
    "dataset_seconds",
    "fraud_probability",
    "decision",
]


def default_log_path() -> Path:
    return PROJECT_ROOT / "data" / "transaction_log.csv"


def load_history(path: Path | None = None) -> pd.DataFrame:
    path = path or default_log_path()
    if not path.exists() or path.stat().st_size == 0:
        return pd.DataFrame(columns=COLUMNS)
    frame = pd.read_csv(path)
    for column in COLUMNS:
        if column not in frame.columns:
            frame[column] = pd.NA
    return frame.loc[:, COLUMNS]


def append_records(records: list[dict], path: Path | None = None) -> int:
    if not records:
        return 0
    path = path or default_log_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    frame = pd.DataFrame(records).reindex(columns=COLUMNS)
    write_header = not path.exists() or path.stat().st_size == 0
    frame.to_csv(path, mode="a", header=write_header, index=False)
    return len(frame)


def new_record(
    source: str,
    amount: float,
    dataset_seconds: float,
    fraud_probability: float,
    decision: str,
) -> dict:
    if decision not in {"allow", "review"}:
        raise ValueError("Decision must be allow or review.")
    return {
        "scored_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        "source": source,
        "amount": round(float(amount), 2),
        "dataset_seconds": round(float(dataset_seconds), 2),
        "fraud_probability": round(float(fraud_probability), 6),
        "decision": decision,
    }


def summarize(frame: pd.DataFrame) -> dict:
    if frame.empty:
        return {"rows": 0, "allow": 0, "review": 0}
    decisions = frame["decision"].astype(str)
    return {
        "rows": int(len(frame)),
        "allow": int((decisions == "allow").sum()),
        "review": int((decisions == "review").sum()),
    }


def clear_history(path: Path | None = None) -> None:
    path = path or default_log_path()
    if path.exists():
        path.unlink()
