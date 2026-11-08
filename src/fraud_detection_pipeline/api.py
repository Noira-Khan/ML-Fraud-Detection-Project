"""Local scoring API. It uses the same cutoff and column order as the screen."""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from fraud_detection_pipeline.scoring import (
    DECISION_THRESHOLD,
    FEATURE_COLUMNS,
    ScoringError,
    score_mapping,
)

app = FastAPI(
    title="Finance Shield scoring",
    description=(
        "Scores one card transaction with the saved model. "
        "A review decision does not decline the payment."
    ),
)


class TransactionRequest(BaseModel):
    features: list[float] = Field(
        ...,
        description="Thirty numbers in order: Time, V1, V2, ... V28, Amount.",
        min_length=30,
        max_length=30,
    )


@app.get("/health")
def health():
    return {
        "status": "ok",
        "features": FEATURE_COLUMNS,
        "threshold": DECISION_THRESHOLD,
        "blocks_payment": False,
    }


@app.post("/predict")
def predict(transaction: TransactionRequest):
    values = dict(zip(FEATURE_COLUMNS, transaction.features))
    try:
        return score_mapping(values)
    except ScoringError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
