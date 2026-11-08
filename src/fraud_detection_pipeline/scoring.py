"""Score a card transaction with the saved XGBoost model.

The model was trained on the public credit-card file in this column order:
Time, V1 ... V28, Amount. Amount and Time were not rescaled.
V1-V28 are anonymous components from that dataset. They are not merchant,
country, or cardholder fields.

The published holdout used a 0.95 cutoff. A score at or above that cutoff
is sent to a person. This module never declines a payment.
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import pandas as pd
from xgboost import XGBClassifier

FEATURE_COLUMNS = ["Time"] + [f"V{i}" for i in range(1, 29)] + ["Amount"]
DECISION_THRESHOLD = 0.95
LEANING_THRESHOLD = 0.50
MAX_BATCH_ROWS = 5000

PROJECT_ROOT = Path(__file__).resolve().parents[2]
NATIVE_MODEL_PATH = PROJECT_ROOT / "models" / "fraud_xgb.json"
PICKLE_MODEL_PATH = PROJECT_ROOT / "best_xgb_model.pkl"
SAMPLE_PATH = PROJECT_ROOT / "samples" / "demo_transactions.csv"

# Holdout printed in notebooks/train_model_LR.ipynb for this saved model.
HOLDOUT_RECORD = {
    "threshold": DECISION_THRESHOLD,
    "test_rows": 56962,
    "test_legitimate": 56864,
    "test_fraud": 98,
    "fraud_precision": 0.93,
    "fraud_recall": 0.82,
    "fraud_f1": 0.87,
    "source": "notebooks/train_model_LR.ipynb evaluation of best_xgb_model.pkl at a 0.95 cutoff",
}

DATASET_RECORD = {
    "rows": 284807,
    "legitimate": 284315,
    "fraud": 492,
    "fraud_share": 0.001727,
    "missing_values": 0,
    "source": "eda_outputs/eda_summary_metrics.txt",
}

EVERYDAY_PURCHASE = {
    "Time": 45000.0,
    "Amount": 42.0,
    "V1": -0.2,
    "V2": 0.15,
    "V3": 0.8,
    "V4": -0.4,
    "V5": 0.1,
    "V6": 0.2,
    "V7": -0.1,
    "V8": 0.05,
    "V9": 0.1,
    "V10": 0.2,
    "V11": -0.2,
    "V12": 0.4,
    "V13": 0.1,
    "V14": 0.3,
    "V15": 0.1,
    "V16": 0.2,
    "V17": 0.1,
    "V18": 0.1,
    "V19": 0.0,
    "V20": 0.0,
    "V21": 0.0,
    "V22": 0.0,
    "V23": 0.0,
    "V24": 0.0,
    "V25": 0.0,
    "V26": 0.0,
    "V27": 0.0,
    "V28": 0.0,
}

SUSPICIOUS_PATTERN = {
    "Time": 75500.0,
    "Amount": 1.0,
    "V1": -2.3,
    "V2": 1.9,
    "V3": -3.8,
    "V4": 4.2,
    "V5": -1.8,
    "V6": -1.2,
    "V7": -3.1,
    "V8": 0.7,
    "V9": -2.5,
    "V10": -5.0,
    "V11": 3.6,
    "V12": -5.4,
    "V13": 0.2,
    "V14": -6.7,
    "V15": 0.1,
    "V16": -3.1,
    "V17": -5.2,
    "V18": -1.7,
    "V19": 0.8,
    "V20": 0.4,
    "V21": 0.6,
    "V22": -0.2,
    "V23": -0.3,
    "V24": -0.4,
    "V25": 0.2,
    "V26": 0.1,
    "V27": 0.5,
    "V28": 0.2,
}


class ScoringError(ValueError):
    """The inputs cannot be scored."""


def frame_from_mapping(values: dict) -> pd.DataFrame:
    missing = [column for column in FEATURE_COLUMNS if column not in values]
    if missing:
        raise ScoringError(
            "Need all 30 inputs in this order: Time, V1 to V28, Amount. "
            f"Missing: {', '.join(missing)}."
        )
    return prepare_frame(pd.DataFrame([{column: values[column] for column in FEATURE_COLUMNS}]))


def prepare_frame(frame: pd.DataFrame) -> pd.DataFrame:
    missing = [column for column in FEATURE_COLUMNS if column not in frame.columns]
    if missing:
        raise ScoringError(
            "The file needs these columns: Time, V1 to V28, Amount. "
            f"Missing: {', '.join(missing)}."
        )
    if len(frame) > MAX_BATCH_ROWS:
        raise ScoringError(
            f"This demo scores up to {MAX_BATCH_ROWS:,} rows at a time. "
            "Split a larger file before uploading it."
        )
    if len(frame) == 0:
        raise ScoringError("There are no rows to score.")

    numeric = frame.loc[:, FEATURE_COLUMNS].apply(pd.to_numeric, errors="coerce")
    bad_rows = numeric.isna().any(axis=1)
    if bad_rows.any():
        first = int(bad_rows.idxmax()) if bad_rows.index.is_unique else int(bad_rows.to_numpy().argmax())
        raise ScoringError(
            f"Row {first + 1} has a blank or non-numeric value. "
            "Every Time, V, and Amount cell has to be a number."
        )
    return numeric.reset_index(drop=True)


@lru_cache(maxsize=1)
def load_model() -> XGBClassifier:
    model = XGBClassifier()
    if NATIVE_MODEL_PATH.exists():
        model.load_model(NATIVE_MODEL_PATH)
        return model
    if PICKLE_MODEL_PATH.exists():
        import joblib

        loaded = joblib.load(PICKLE_MODEL_PATH)
        NATIVE_MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
        loaded.get_booster().save_model(NATIVE_MODEL_PATH)
        model.load_model(NATIVE_MODEL_PATH)
        return model
    raise ScoringError(
        "No model file found. Expected models/fraud_xgb.json or best_xgb_model.pkl "
        "in the project folder."
    )


def fraud_probabilities(frame: pd.DataFrame) -> list[float]:
    ready = prepare_frame(frame)
    probabilities = load_model().predict_proba(ready)[:, 1]
    return [float(value) for value in probabilities]


def decision_for(probability: float, threshold: float = DECISION_THRESHOLD) -> str:
    if probability >= threshold:
        return "review"
    return "allow"


def summary_for(probability: float, threshold: float = DECISION_THRESHOLD) -> str:
    percent = probability * 100
    if probability >= threshold:
        return (
            f"Send this to a person. The fraud score is {percent:.2f}%, "
            f"which is at or above the {threshold:.0%} cutoff. "
            "This demo does not decline the card. A reviewer confirms it before anyone blocks the payment."
        )
    if probability >= LEANING_THRESHOLD:
        return (
            f"Allow the payment. The score is {percent:.2f}%, so the model leans suspicious, "
            f"but it is still under the {threshold:.0%} cutoff used in the evaluation. "
            "A reviewer can choose to look. The payment is not blocked."
        )
    return (
        f"Allow the payment. The fraud score is {percent:.2f}%, "
        f"under the {threshold:.0%} cutoff. It would not be sent for review."
    )


def reasons_for(values: dict, probability: float) -> list[str]:
    notes: list[str] = []
    checks = (
        (
            "V14",
            lambda value: value < -3,
            "V14 is strongly negative. This saved model puts most of its weight on V14.",
        ),
        (
            "V4",
            lambda value: value > 2,
            "V4 is high. It is the second-strongest feature in this model.",
        ),
        (
            "V12",
            lambda value: value < -3,
            "V12 is far below the usual range for a legitimate transaction in this dataset.",
        ),
        (
            "V17",
            lambda value: value < -3,
            "V17 is strongly negative. In the original file, low V17 lined up with fraud.",
        ),
        (
            "V10",
            lambda value: value < -3,
            "V10 is strongly negative, another pattern that showed up with fraud.",
        ),
    )
    for name, rule, message in checks:
        raw = values.get(name, 0.0)
        try:
            number = float(raw)
        except (TypeError, ValueError):
            continue
        if rule(number):
            notes.append(message)

    if decision_for(probability) == "review" and not notes:
        notes.append(
            "No single feature crossed a simple warning line, but the 30 inputs together cleared 95%."
        )
    if decision_for(probability) == "allow" and not notes:
        notes.append(
            "None of the main warning features (V14, V4, V12, V17, V10) crossed a simple line."
        )
    notes.append(
        "V1 to V28 are anonymous. Changing only the amount usually will not flip the decision."
    )
    return notes[:4]


def score_mapping(values: dict, threshold: float = DECISION_THRESHOLD) -> dict:
    frame = frame_from_mapping(values)
    probability = fraud_probabilities(frame)[0]
    return {
        "fraud_probability": round(probability, 6),
        "threshold": threshold,
        "decision": decision_for(probability, threshold),
        "summary": summary_for(probability, threshold),
        "reasons": reasons_for(values, probability),
        "blocks_payment": False,
    }


def score_table(frame: pd.DataFrame, threshold: float = DECISION_THRESHOLD) -> pd.DataFrame:
    ready = prepare_frame(frame)
    probabilities = fraud_probabilities(ready)
    scored = ready.copy()
    scored["fraud_probability"] = [round(value, 6) for value in probabilities]
    scored["decision"] = [decision_for(value, threshold) for value in probabilities]
    return scored
