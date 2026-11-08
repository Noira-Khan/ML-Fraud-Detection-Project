# Implementation by phases — Finance Shield

Date: 8 November 2026.

Each phase uses only what the previous phase left behind, plus files you can actually obtain. A phase is not started by writing a dashboard number for a system that is not connected.

## Phase 1 — A score you can run locally

**Status: done in this repository.**

Resources used:

- `best_xgb_model.pkl`, exported to `models/fraud_xgb.json`
- the holdout printout in `notebooks/train_model_LR.ipynb`
- the class counts in `eda_outputs/eda_summary_metrics.txt`
- Python, Streamlit, FastAPI, XGBoost

Work:

- One scorer for the screen and the API.
- Column order fixed to `Time`, `V1`–`V28`, `Amount`, unscaled.
- Decision cutoff set to 95%, the cutoff behind the 0.93 / 0.82 / 0.87 holdout.
- Two examples and `samples/demo_transactions.csv`, so the Kaggle file is not required.
- Removed the screen figures that were not measured (a live transaction count, a dollar saving, a 41 ms latency, a 0.98 ROC-AUC).
- Reasons written from the features this model weights, in words a reviewer can read.
- Upload capped at 5,000 rows, with a clear error when a column or a cell is bad.

Done when:

- `pytest` passes.
- Everyday purchase returns Allow. Suspicious pattern returns Review.
- The screen says a review does not decline the card.

## Phase 2 — A training run you can repeat

**Status: not started. Needs a file this git repository does not contain.**

Resource required on the machine, not in git: the public credit-card CSV (Kaggle / ULB), saved locally as `CreditCard.csv`. It is listed in `.gitignore` on purpose.

Work, when that file is present:

- One script that splits with the same rule as the notebook (`test_size` 0.2, `stratify`, `random_state` 42), fits only on the training rows, and writes `models/fraud_xgb.json`.
- Write a small `metrics.json` with the confusion-matrix counts at the 95% cutoff, plus fraud precision, recall, and F1. The current notebook prints 0.93 and 0.82 to two decimals and does not save the four counts for the tuned model.
- Keep SMOTE, if used, on the training rows only.
- Do not record the rebalanced cross-validation F1 as the model’s result.
- Leave `src/frontend.py` pointed at the scorer. The screen should not grow a training button.

Done when a second machine with the CSV can reproduce the score file and the metrics file without opening the notebooks in order.

## Phase 3 — A review note a person can overturn

**Status: not started. Still local. No new dataset.**

The product gap after Phase 1: the screen says Review, and then nothing records what the person did.

Work:

- A local log (a CSV or SQLite file, gitignored) with the score, the decision, the time, and a reviewer choice: agree, or allow anyway.
- The card is still not declined by the software. “Allow anyway” is the override.
- The model record page can later show how often reviewers disagreed. That count starts at zero until someone uses the log. It is not backfilled with a fake rate.

Done when a reviewer can open a Review row, choose allow anyway, and see that choice on a later visit to the same local file.

## Phase 4 — A feed that is not a CSV upload

**Status: not started. Blocked on a source this project does not have.**

A real-time claim needs a stream of payments, an owner of that stream, and a latency budget someone can measure. This repository has a static public file and a saved model. Phase 4 does not begin by adding a “41 ms” label.

If a feed exists later, the same scorer stays the decision point: same 30 columns, same 95% cutoff, same rule that a high score goes to a person. New work would be the adapter in front of the scorer, plus a count of scores, misses, and reviewer overrides from that feed.

Out of every phase until a real case system exists: an LLM copilot, a cloud deploy as a success metric, and any screen that reports money saved without a ledger.
