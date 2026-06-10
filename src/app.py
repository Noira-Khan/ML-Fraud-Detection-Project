from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import numpy as np
import time
from functools import wraps
import os
import sys

# --- Path Resolution for Imports ---
# Ensures Python can find 'predict.py' even if you run uvicorn from the project root
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from predict import FraudPredictor

# --- API Initialization ---
app = FastAPI(
    title="Fraud Detection API",
    description="Real-time inference engine with Explainable AI (SHAP).",
    version="1.0.0"
)

# --- Model Loading ---
# Resolving the model path dynamically to match predict.py and train.py
model_absolute_path = os.path.join(current_dir, 'best_xgb_model.pkl')

# Initialize the predictor once at startup
predictor = FraudPredictor(model_path=model_absolute_path)

# --- Data Schemas ---
class TransactionData(BaseModel):
    features: list[float]

# --- Utilities ---
def log_inference_time(func):
    """Decorator to log request processing time."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        result = await func(*args, **kwargs)
        process_time = time.time() - start_time
        print(f"Inference processed in {process_time:.4f}s")
        return result
    return wrapper

# --- Endpoints ---
@app.post("/predict")
@log_inference_time
async def make_prediction(data: TransactionData):
    try:
        # 1. Validate feature count
        if len(data.features) != 30:
            raise ValueError(f"Expected 30 features, received {len(data.features)}")
            
        feature_array = np.array(data.features)
        
        # 2. Get probability score and SHAP reasons
        fraud_prob = predictor.predict_probability(feature_array)
        top_reasons = predictor.get_reasons(feature_array)
        
        # 3. Determine strict classification (Threshold = 0.5)
        is_fraud = bool(fraud_prob >= 0.5)
        
        # 4. Return formatted response
        return {
            "status": "success",
            "fraud_probability": round(fraud_prob, 4),
            "is_fraud": is_fraud,
            "risk_level": "High" if is_fraud else "Low",
            "top_drivers": top_reasons
        }
        
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")