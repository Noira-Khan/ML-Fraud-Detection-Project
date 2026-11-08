# Finance Shield

A card risk desk that scores one card payment, or a small file of payments, and says **Allow** or **Review**.

A Review case does not decline the card. At 95% or above, the screen also shows the phone alert and the email the customer would get at that moment. That message is a preview. Nothing is sent.

The original public dataset is not required. The saved model is already in `models/fraud_xgb.json`.

The model only sees `Time`, `V1`–`V28`, and `Amount`. Those V columns are anonymous. It cannot see a merchant, a country, or a cardholder.

## What a score means

On the holdout in `notebooks/train_model_LR.ipynb`, a **95%** cutoff gave about **0.93 fraud precision**, **0.82 fraud recall**, and **0.87 fraud F1** (98 fraud cases in the test split). Accuracy on that file is about 99.8% even for a model that never catches fraud, so the screen does not lead with accuracy.

| Score | What the banker sees | What the customer gets |
| --- | --- | --- |
| Under 95% | Allow. The payment can go through. | No message. |
| 95% or more | Review. The case is filed on the queue. | A phone alert and an email, shown here as a preview. The card is not blocked yet. |

## Run the screen

```bash
pip install -r requirements.txt
streamlit run src/frontend.py
```

The desk has five pages:

- **Payment queue** — cases scored on this computer. It starts empty.
- **Single payment** — Everyday purchase or Suspicious pattern.
- **Batch file** — `samples/demo_transactions.csv`. Each row has a short **Meaning** note. The decision sheet shows the score on the same page.
- **Model record** — the holdout precision, recall, and F1.
- **Operating rules** — the path from a row to Allow or Review.

## Run the API

```bash
uvicorn app:app --app-dir src
```

`GET /health`  
`POST /predict` with 30 numbers in this order: `Time`, `V1` … `V28`, `Amount`.

The API returns the score and the decision. It does not send the customer message. `blocks_payment` is always false.

## Documents

- [Product requirements](docs/PRD.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Implementation by phases](docs/IMPLEMENTATION-PHASES.md)
- [Screen style](docs/STYLE.md)

## Tests

```bash
pytest
```

## What is not in this repository

`CreditCard.csv` and the `.npy` training arrays stay on your machine. Retraining is optional. `python src/train.py` explains that and does not pretend the dataset is present. The queue file `data/transaction_log.csv` is created on your machine and is not committed.
