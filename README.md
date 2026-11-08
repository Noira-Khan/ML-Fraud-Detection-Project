# Finance Shield

A local demo that scores one card payment and says **Allow** or **Review**.

A review flag does not decline the card. The original public dataset is not required to run the demo. The saved model is already in `models/fraud_xgb.json`.

The model only sees `Time`, `V1`–`V28`, and `Amount`. Those V columns are anonymous. It cannot see a merchant, a country, or a cardholder.

## What a score means

On the holdout in `notebooks/train_model_LR.ipynb`, a **95%** cutoff gave about **0.93 fraud precision**, **0.82 fraud recall**, and **0.87 fraud F1** (98 fraud cases in the test split). Accuracy on that file is about 99.8% even for a model that never catches fraud, so the screen does not lead with accuracy.

## Run the screen

```bash
pip install -r requirements.txt
streamlit run src/frontend.py
```

Open **Check one payment** and choose **Everyday purchase** or **Suspicious pattern**.

## Run the API

```bash
uvicorn app:app --app-dir src
```

`GET /health`  
`POST /predict` with 30 numbers in this order: `Time`, `V1` … `V28`, `Amount`.

## Documents

- [Product requirements](docs/PRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Implementation by phases](docs/IMPLEMENTATION-PHASES.md)

## Tests

```bash
pytest
```

## What is not in this repository

`CreditCard.csv` and the `.npy` training arrays stay on your machine. Retraining is optional. `python src/train.py` explains that and does not pretend the dataset is present.
