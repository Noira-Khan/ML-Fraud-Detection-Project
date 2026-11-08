"""Small wrapper kept so older scripts can still call FraudPredictor."""

from __future__ import annotations

import numpy as np

from fraud_detection_pipeline.scoring import FEATURE_COLUMNS, score_mapping


class FraudPredictor:
    def __init__(self, model_path: str | None = None):
        # The path argument is accepted for older callers. Loading uses models/fraud_xgb.json.
        self.model_path = model_path

    def predict_probability(self, feature_array: np.ndarray) -> float:
        values = _values_from_array(feature_array)
        return float(score_mapping(values)["fraud_probability"])

    def get_reasons(self, feature_array: np.ndarray) -> list[str]:
        values = _values_from_array(feature_array)
        return score_mapping(values)["reasons"]


def _values_from_array(feature_array: np.ndarray) -> dict:
    array = np.asarray(feature_array, dtype=float)
    if array.ndim == 2:
        array = array[0]
    if array.shape[0] != len(FEATURE_COLUMNS):
        raise ValueError(
            f"Expected {len(FEATURE_COLUMNS)} features (Time, V1-V28, Amount). Got {array.shape[0]}."
        )
    return dict(zip(FEATURE_COLUMNS, array.tolist()))


if __name__ == "__main__":
    from fraud_detection_pipeline.scoring import EVERYDAY_PURCHASE, SUSPICIOUS_PATTERN

    for name, example in ("everyday", EVERYDAY_PURCHASE), ("suspicious", SUSPICIOUS_PATTERN):
        result = score_mapping(example)
        print(name, result["decision"], result["fraud_probability"])
