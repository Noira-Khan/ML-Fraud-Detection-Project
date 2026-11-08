import pandas as pd
import pytest
from fastapi.testclient import TestClient

from fraud_detection_pipeline.api import app
from fraud_detection_pipeline.scoring import (
    DECISION_THRESHOLD,
    EVERYDAY_PURCHASE,
    FEATURE_COLUMNS,
    SAMPLE_PATH,
    SUSPICIOUS_PATTERN,
    ScoringError,
    prepare_frame,
    score_mapping,
    score_table,
)


def test_examples_follow_the_published_cutoff():
    everyday = score_mapping(EVERYDAY_PURCHASE)
    suspicious = score_mapping(SUSPICIOUS_PATTERN)
    assert everyday["decision"] == "allow"
    assert everyday["fraud_probability"] < DECISION_THRESHOLD
    assert suspicious["decision"] == "review"
    assert suspicious["fraud_probability"] >= DECISION_THRESHOLD
    assert everyday["blocks_payment"] is False
    assert suspicious["blocks_payment"] is False


def test_feature_order_is_time_then_v_then_amount():
    assert FEATURE_COLUMNS[0] == "Time"
    assert FEATURE_COLUMNS[-1] == "Amount"
    assert FEATURE_COLUMNS[1:29] == [f"V{i}" for i in range(1, 29)]


def test_sample_file_scores_both_decisions():
    scored = score_table(pd.read_csv(SAMPLE_PATH))
    assert list(scored["decision"]) == ["allow", "review"]


def test_missing_column_is_explained():
    with pytest.raises(ScoringError, match="Missing"):
        prepare_frame(pd.DataFrame({"Amount": [1.0]}))


def test_api_health_and_predict():
    client = TestClient(app)
    health = client.get("/health")
    assert health.status_code == 200
    assert health.json()["threshold"] == DECISION_THRESHOLD
    features = [EVERYDAY_PURCHASE[column] for column in FEATURE_COLUMNS]
    response = client.post("/predict", json={"features": features})
    assert response.status_code == 200
    assert response.json()["decision"] == "allow"
    bad = client.post("/predict", json={"features": [0.0, 1.0]})
    assert bad.status_code == 422
