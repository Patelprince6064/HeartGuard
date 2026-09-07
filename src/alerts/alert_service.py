"""Emergency alert service module for HeartGuard.

Provides function signatures for sending alerts.
Actual Twilio implementation will be done in Phase 10.
"""

from datetime import datetime
from typing import Any, Optional

from src.utils.logger import get_logger

logger = get_logger(__name__)


def send_sms_alert(
    phone_number: str,
    message: str,
) -> dict[str, Any]:
    """Send an SMS alert via Twilio.

    Placeholder for future implementation.

    Args:
        phone_number: Recipient phone number.
        message: Alert message text.

    Returns:
        Dictionary with delivery status.

    Raises:
        NotImplementedError: Always, until Phase 10.
    """
    raise NotImplementedError("SMS alert sending will be implemented in Phase 10")


def check_alert_threshold(risk_score: float, threshold: float = 85.0) -> bool:
    """Check if risk score exceeds alert threshold.

    Placeholder for future implementation.

    Args:
        risk_score: Patient risk score.
        threshold: Alert threshold value.

    Returns:
        True if alert should be sent.
    """
    logger.warning("check_alert_threshold is a placeholder")
    return risk_score >= threshold


def log_alert(
    patient_id: str,
    risk_score: float,
    alert_type: str,
    status: str = "pending",
) -> dict[str, Any]:
    """Log an alert to the alerts directory.

    Placeholder for future implementation.

    Args:
        patient_id: Patient identifier.
        risk_score: Risk score that triggered alert.
        alert_type: Type of alert.
        status: Alert delivery status.

    Returns:
        Dictionary with alert log entry.
    """
    alert_entry = {
        "timestamp": datetime.now().isoformat(),
        "patient_id": patient_id,
        "risk_score": risk_score,
        "alert_type": alert_type,
        "status": status,
    }

    logger.info(f"Alert logged for patient {patient_id}: {alert_type}")
    return alert_entry
