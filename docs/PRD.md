# Product requirements — Finance Shield

Status: local demo, matched to the model and files already in this repository.  
Date: 8 November 2026.  
Owner: Noira Khan.

This document describes the product the code now is, and the boundary around it. It does not describe a live bank deployment.

## Problem

Card fraud is rare. On the public file used for this project, 492 of 284,807 payments are fraud (0.1727%). A model that calls every payment legitimate is about 99.83% accurate and stops nothing.

The product has to catch fraud at the moment a payment is scored, and it must not treat a good customer as a fraud. A false decline at a till is a customer problem, not only a model problem. This version does that by sending a high score to a person. It does not decline the card.

## User

The person in front of this demo is a reviewer, or someone learning the reviewer’s job. They are not the cardholder. They are not an executive looking at a live book of business.

The cardholder is affected only if a later system blocks the payment. This demo never does that.

## Decision

For one payment, the product answers:

> Is this score high enough to send to a person, or should it be allowed through?

| Score | What the screen says | What happens to the money |
| --- | --- | --- |
| 95% or more | Review | Nothing is declined. A person would confirm before a block. |
| 50% to just under 95% | Allow, and say the model leans suspicious | The payment is not queued by the published cutoff. A person may still look. |
| Under 50% | Allow | It would not be sent for review. |

95% is the cutoff that produced the holdout numbers below. It is a product choice already made in the training notebook, not a new invention for the screen.

## What the model may do

- Read thirty numbers in one fixed order: `Time`, `V1` through `V28`, `Amount`.
- Return a fraud score between 0 and 1.
- Name the few anonymous features that crossed a simple warning line, especially V14, which carries most of this model’s weight.

## What the model must never do

- Decline, reverse, or hold a real payment. The API field `blocks_payment` is always false.
- Pretend V1–V28 are merchant, device, city, or cardholder fields. They are anonymous components from the public dataset.
- Lead with accuracy.
- Show a live “transactions today” or “dollars saved” figure. This repository has no live feed, so those numbers were removed from the screen.
- Treat the 0.9999 cross-validation score as the result. That score was computed on rebalanced training rows. The holdout is the result that counts.

## How we know it was wrong

On the untouched test split printed in `notebooks/train_model_LR.ipynb` (56,962 payments, 98 fraud):

| Metric on the fraud class | Printed result at the 95% cutoff |
| --- | --- |
| Precision | 0.93 |
| Recall | 0.82 |
| F1 | 0.87 |

Who pays:

- A missed fraud (the recall gap) is money that leaves.
- A false review (the precision gap) is a good payment sent to a person. In this demo that person can let it through. The cost is the reviewer’s time, not an automatic decline.
- About 18% of the holdout fraud cases were still missed at this cutoff. That miss is visible. It is not hidden inside 99% accuracy.

Logistic regression on the same split reached about 0.92 recall and only about 0.06 precision. It is the comparison that shows why the tree model was kept: catching fraud by flagging a huge share of good payments fails the stakeholder note.

## Scope of this version

In:

- A screen with two worked examples, so nobody has to type 28 anonymous numbers to see both decisions.
- A two-row sample file, and a CSV upload capped at 5,000 rows.
- The same score through `POST /predict`.
- Plain language for Allow and Review.
- The model file in `models/fraud_xgb.json`, so the demo runs without the 284,807-row dataset.

Out:

- A connection to a card network, a bank ledger, or a case system.
- Training inside the demo. The public CSV is not in git.
- SHAP as a required install. The short reasons use the features this model actually weights.
- A claim that the demo is real-time production scoring. It is a local score of a row you provide.

## Success for this version

Someone with Python and this repository can, without downloading the Kaggle file:

1. Open the screen.
2. Score the everyday example and see Allow.
3. Score the suspicious example and see Review.
4. Read a reason that does not invent a merchant or a city.
5. Read the holdout precision and recall next to a sentence about why accuracy misleads.

## Open questions

- The holdout precision and recall were printed to two decimal places (0.93 and 0.82). The notebook output does not include a full confusion-matrix count for the tuned model. A later training run should save that count.
- No ROC-AUC was printed for the saved model. It is not quoted.
- Whether a reviewer override should be stored is a later phase. This version only shows the decision.
