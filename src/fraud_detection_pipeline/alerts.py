"""When a score should tell the customer.

A message is prepared only when the case is Review, which means the score
is at or above the 95% cutoff. The card is not declined by this step.
"""

from __future__ import annotations


def should_notify_customer(decision: str) -> bool:
    return decision == "review"


def customer_message(amount: float) -> dict[str, str]:
    money = f"{float(amount):,.2f}"
    return {
        "when": "The moment the score reaches 95%.",
        "push": (
            f"Did you just use your card for {money}? "
            "If yes, you can ignore this. If no, open your banking app and tap No. "
            "We have not blocked your card."
        ),
        "subject": "Please check a card payment",
        "email": (
            f"Hello,\n\n"
            f"We are checking a card payment of {money} because it looked unusual.\n"
            f"If you made this payment, no action is needed.\n"
            f"If you did not make it, open your banking app and tell us. "
            f"We have not blocked your card yet.\n\n"
            f"Finance Shield"
        ),
    }


def banker_explanation(decision: str, score_percent: float) -> str:
    if should_notify_customer(decision):
        return (
            f"This payment looks suspicious. The score is {score_percent:.2f}%, "
            "which is at the 95% line or above. At that moment two things happen: "
            "the case comes to you, and the customer gets a phone alert and an email. "
            "You still make the call. The card is not blocked yet. "
            "That early message is how the customer can stop a payment they did not make."
        )
    return (
        f"This payment looks normal. The score is {score_percent:.2f}%, under 95%. "
        "No message is sent to the customer. The payment can go through."
    )
