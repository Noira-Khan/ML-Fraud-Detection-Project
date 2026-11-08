from fraud_detection_pipeline.alerts import (
    banker_explanation,
    customer_message,
    should_notify_customer,
)
from fraud_detection_pipeline.scoring import EVERYDAY_PURCHASE, SUSPICIOUS_PATTERN, score_mapping


def test_only_a_review_tells_the_customer():
    everyday = score_mapping(EVERYDAY_PURCHASE)
    suspicious = score_mapping(SUSPICIOUS_PATTERN)
    assert should_notify_customer(everyday["decision"]) is False
    assert should_notify_customer(suspicious["decision"]) is True
    message = customer_message(SUSPICIOUS_PATTERN["Amount"])
    assert "have not blocked" in message["push"].lower() or "have not blocked" in message["email"].lower()
    assert "95%" in banker_explanation("review", suspicious["fraud_probability"] * 100)
    assert "No message" in banker_explanation("allow", everyday["fraud_probability"] * 100)
