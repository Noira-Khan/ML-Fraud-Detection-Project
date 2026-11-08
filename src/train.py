"""Retrain only when the public credit-card file is already on this machine.

That file is not in this repository. The running demo uses models/fraud_xgb.json,
which was exported from best_xgb_model.pkl. You do not need to retrain to use the screen or the API.
"""

from __future__ import annotations

import sys
from pathlib import Path

import joblib
import numpy as np
import xgboost as xgb
from sklearn.metrics import classification_report

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT / "src") not in sys.path:
    sys.path.insert(0, str(ROOT / "src"))

from fraud_detection_pipeline.scoring import DECISION_THRESHOLD, FEATURE_COLUMNS  # noqa: E402


class FraudDetectionTrainer:
    def __init__(self, data_dir: Path, model_save_path: Path):
        self.data_dir = Path(data_dir)
        self.model_save_path = Path(model_save_path)
        self.model = None

    def load_data(self) -> None:
        required = ["X_train.npy", "y_train.npy", "X_test.npy", "y_test.npy"]
        missing = [name for name in required if not (self.data_dir / name).exists()]
        if missing:
            raise FileNotFoundError(
                "Training arrays are not in the repository. "
                "Build them locally from CreditCard.csv before calling load_data. "
                f"Missing: {', '.join(missing)}."
            )
        self.X_train = np.load(self.data_dir / "X_train.npy")
        self.y_train = np.load(self.data_dir / "y_train.npy")
        self.X_test = np.load(self.data_dir / "X_test.npy")
        self.y_test = np.load(self.data_dir / "y_test.npy")
        if self.X_train.shape[1] != len(FEATURE_COLUMNS):
            raise ValueError(
                f"Expected {len(FEATURE_COLUMNS)} columns in order {FEATURE_COLUMNS[0]} ... Amount."
            )

    def train_model(self, best_params: dict) -> None:
        self.model = xgb.XGBClassifier(**best_params, random_state=42)
        self.model.fit(self.X_train, self.y_train)

    def evaluate_model(self) -> None:
        probabilities = self.model.predict_proba(self.X_test)[:, 1]
        predictions = (probabilities >= DECISION_THRESHOLD).astype(int)
        print(classification_report(self.y_test, predictions, target_names=["Legitimate", "Fraud"]))

    def save_model(self) -> None:
        self.model_save_path.parent.mkdir(parents=True, exist_ok=True)
        self.model.get_booster().save_model(self.model_save_path)
        joblib.dump(self.model, ROOT / "best_xgb_model.pkl")
        print(f"Saved {self.model_save_path}")


if __name__ == "__main__":
    print(
        "This demo already has a model at models/fraud_xgb.json. "
        "Retraining needs CreditCard.csv and the .npy splits on your machine. "
        "Those files are intentionally not in git."
    )
    print("Column order if you do retrain:", ", ".join(FEATURE_COLUMNS))
    print(f"Judge fraud precision and recall at a cutoff of {DECISION_THRESHOLD}, not accuracy.")
