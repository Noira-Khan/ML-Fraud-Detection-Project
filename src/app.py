from fastapi import FastAPI
from pydantic import BaseModel
import numpy as np

from predict import FraudPredictor

app = FastAPI(
    title="Fraud Detection API"
)

predictor = FraudPredictor(
    model_path="best_xgb_model.pkl"
)

class TransactionData(BaseModel):
    features: list[float]

@app.post("/predict")
async def predict(data: TransactionData):

    feature_array = np.array(data.features)

    fraud_probability = predictor.predict_probability(
        feature_array
    )

    return {
        "fraud_probability": round(
            fraud_probability, 4
        ),
        "is_fraud": fraud_probability >= 0.5
    }