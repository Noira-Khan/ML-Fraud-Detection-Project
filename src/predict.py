import joblib
import numpy as np
import shap
import os

class FraudPredictor:
    def __init__(self, model_path: str):
        """Loads the serialized model and SHAP explainer into memory."""
        try:
            self.model = joblib.load(model_path)
            # Initialize the SHAP explainer once when the model loads
            self.explainer = shap.TreeExplainer(self.model)
            print("Model and SHAP Explainer loaded successfully.")
        except FileNotFoundError:
            raise Exception(f"Model file not found at {model_path}.")

    def predict_probability(self, feature_array: np.ndarray) -> float:
        """Takes a 2D numpy array of features and returns the probability of fraud."""
        if feature_array.ndim == 1:
            feature_array = feature_array.reshape(1, -1)
            
        # predict_proba returns [[prob_class_0, prob_class_1]]
        probabilities = self.model.predict_proba(feature_array)
        return float(probabilities[0][1])

    def get_reasons(self, feature_array: np.ndarray) -> list:
        """Calculates the top 3 features driving this specific prediction using SHAP."""
        if feature_array.ndim == 1:
            feature_array = feature_array.reshape(1, -1)
            
        # Calculate SHAP values for this specific transaction
        shap_values = self.explainer.shap_values(feature_array)[0]
        
        # Recreate feature names to match the Kaggle Credit Card dataset
        feature_names = [f"V{i}" for i in range(1, 29)] + ["Amount", "Time"]
        
        # Map the SHAP values to the feature names
        contributions = []
        for name, shap_val in zip(feature_names, shap_values):
            contributions.append({
                "feature": name,
                "impact": "Increased Fraud Risk" if shap_val > 0 else "Lowered Fraud Risk",
                "magnitude": abs(float(shap_val))
            })
            
        # Sort by the strongest drivers (highest magnitude) and return the top 3
        contributions.sort(key=lambda x: x["magnitude"], reverse=True)
        return contributions[:3]

if __name__ == "__main__":
    # Local testing execution using dynamic absolute path
    current_dir = os.path.dirname(os.path.abspath(__file__))
    model_path = os.path.join(current_dir, 'best_xgb_model.pkl')
    
    predictor = FraudPredictor(model_path=model_path)
    dummy_features = np.zeros(30) 
    
    prob = predictor.predict_probability(dummy_features)
    reasons = predictor.get_reasons(dummy_features)
    
    print(f"Fraud Probability Score: {prob:.4f}")
    print("Top Drivers:", reasons)
    