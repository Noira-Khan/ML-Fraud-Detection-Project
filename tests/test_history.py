import pandas as pd

from fraud_detection_pipeline.history import (
    append_records,
    clear_history,
    load_history,
    new_record,
    summarize,
)
from fraud_detection_pipeline.scoring import EVERYDAY_PURCHASE, score_mapping


def test_history_round_trip(tmp_path):
    path = tmp_path / "transaction_log.csv"
    result = score_mapping(EVERYDAY_PURCHASE)
    saved = append_records(
        [
            new_record(
                source="Everyday purchase",
                amount=EVERYDAY_PURCHASE["Amount"],
                dataset_seconds=EVERYDAY_PURCHASE["Time"],
                fraud_probability=result["fraud_probability"],
                decision=result["decision"],
            )
        ],
        path,
    )
    assert saved == 1
    loaded = load_history(path)
    assert list(loaded["decision"]) == ["allow"]
    assert summarize(loaded) == {"rows": 1, "allow": 1, "review": 0}
    clear_history(path)
    assert load_history(path).empty


def test_missing_log_is_empty(tmp_path):
    frame = load_history(tmp_path / "missing.csv")
    assert isinstance(frame, pd.DataFrame)
    assert summarize(frame)["rows"] == 0
