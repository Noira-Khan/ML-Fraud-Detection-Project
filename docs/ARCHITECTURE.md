# Architecture — Finance Shield

Date: 8 November 2026.

This is the path that actually runs. The sketch in `assets/architecture.png` is the earlier pipeline drawing. The demo stops at local scoring.

## What you need on the machine

- Python 3.10 or newer.
- The packages in `requirements.txt`.
- `models/fraud_xgb.json` (already in the repository).

You do not need `CreditCard.csv`, the `.npy` splits, Optuna, imbalanced-learn, or SHAP to score a payment.

## Flow

```text
Screen or CSV or POST /predict
        |
        v
fraud_detection_pipeline.scoring
  check the 30 columns
  order: Time, V1, V2, ... V28, Amount
        |
        v
models/fraud_xgb.json
  XGBoost, 30 inputs, fraud score
        |
        v
cutoff 0.95
        |
        +--> Allow
        +--> Review
                |
                v
        short reasons (V14, V4, V12, V17, V10)
        payment is not declined
```

The screen (`src/frontend.py`) and the API (`src/fraud_detection_pipeline/api.py`) both call `score_mapping` or `score_table`. They do not each contain a separate model.

## Column order

The saved model was fit on the public file after dropping `Class`, with no rescaling:

`Time`, `V1` … `V28`, `Amount`.

An earlier preprocessing notebook scales Amount and Time and moves them to the front. That transformed frame is **not** what was saved into `X_train.npy` or into this model. The scorer does not apply that scaling. Doing so would score a different problem than the one the model learned.

## Model file

`best_xgb_model.pkl` is the original export. `models/fraud_xgb.json` is the same booster written with XGBoost’s own save format, which is safer to load on a newer XGBoost. The scorer prefers the JSON file.

Trained settings read from the pickle: `max_depth` 7, `learning_rate` about 0.273, `n_estimators` 269. Those match the Optuna result in `notebooks/model_tuning.ipynb`. Training used SMOTE on the training rows only. The test rows were not rebalanced.

Feature weight inside the saved model, highest first: V14 (about 0.69), then V4, V12, V17. The reason text follows that order. Amount is not treated as the main driver.

## API

Run from the project folder:

```bash
uvicorn app:app --app-dir src
```

| Call | Body | Result |
| --- | --- | --- |
| `GET /health` | none | feature order, cutoff 0.95, `blocks_payment: false` |
| `POST /predict` | `{ "features": [30 numbers] }` | score, decision, summary, reasons |

A short list of features is rejected. The order is the contract.

## Screen

| Page | Job |
| --- | --- |
| Start here | Says this is a local demo, and shows file counts from `eda_outputs/eda_summary_metrics.txt`. |
| Check one payment | Two examples. Advanced V fields stay closed. |
| Check a file | Included two-row sample, or an upload up to 5,000 rows. |
| Model record | Holdout precision, recall, and F1. Accuracy is explained, not celebrated. |
| How it fits together | The five steps above, plus the original sketch. |

## What the notebooks still are

The notebooks are the research trail. They are not the runtime.

| Notebook | Role |
| --- | --- |
| `DataLoad.ipynb` | Read `CreditCard.csv`. |
| `EDA.ipynb` | Wrote `eda_outputs/eda_summary_metrics.txt`. |
| `PreProcessing.ipynb` | A scaling experiment. Not the training matrix. |
| `train_model_LR.ipynb` | Split, logistic regression, trees, and the 0.95 evaluation of the saved model. |
| `model_tuning.ipynb` | Optuna on rebalanced training rows, then the pickle export. |

`src/train.py` refuses to invent training arrays. It prints the column order and the cutoff, and stops.

## Tests

`tests/test_scoring.py` loads the real model and checks:

- the everyday example is Allow and the suspicious example is Review
- the sample file returns both decisions
- a missing column gets a plain error
- `/health` and `/predict` agree with the scorer

`tests/test_sample.py` still checks that the pipeline entrypoint prints a start line. That entrypoint does not score a payment.
