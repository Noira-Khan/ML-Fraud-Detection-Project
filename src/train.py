import os
import numpy as np
import xgboost as xgb
import joblib
from sklearn.metrics import classification_report

class FraudDetectionTrainer:
    def __init__(self, data_dir: str, model_save_path: str):
        """
        __init__ method initializes the class with paths.
        self-variables store the state of the object.
        """
        self.data_dir = data_dir
        self.model_save_path = model_save_path
        self.model = None

    def load_data(self):
        """Loads numpy arrays generated from the Jupyter notebooks."""
        print("Loading training data...")
        self.X_train = np.load(f"{self.data_dir}/X_train.npy")
        self.y_train = np.load(f"{self.data_dir}/y_train.npy")
        self.X_test = np.load(f"{self.data_dir}/X_test.npy")
        self.y_test = np.load(f"{self.data_dir}/y_test.npy")

    def train_model(self, best_params: dict):
        """Trains the XGBoost model using the optimized hyperparameters."""
        print("Training model...")
        self.model = xgb.XGBClassifier(**best_params, random_state=42)
        self.model.fit(self.X_train, self.y_train)

    def evaluate_model(self):
        """Runs predictions and prints the classification report."""
        preds = self.model.predict(self.X_test)
        print("\nEvaluation Results:")
        print(classification_report(self.y_test, preds))

    def save_model(self):
        """Serializes the trained model to disk."""
        joblib.dump(self.model, self.model_save_path)
        print(f"Model successfully saved to {self.model_save_path}")

if __name__ == "__main__":
   
    params = {
        'max_depth': 6,          
        'learning_rate': 0.05,   
        'n_estimators': 200,     
        'objective': 'binary:logistic',
        'eval_metric': 'auc',          
        'scale_pos_weight': 577,       # Forces model to treat 1 fraud case as equal to 577 safe cases
        'verbosity': 0
    }
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(current_dir)
    
    data_path = project_root
    model_path = os.path.join(current_dir, 'best_xgb_model.pkl')
    
    trainer = FraudDetectionTrainer(data_dir=data_path, model_save_path=model_path)
    trainer.load_data()
    trainer.train_model(params)
    trainer.evaluate_model()
    trainer.save_model()