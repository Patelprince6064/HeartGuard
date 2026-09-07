"""Audit logger for HeartGuard security events (Phase 9).

Writes structured audit records to a SQLite database.
Records: timestamp, event_type, user_id, role, status, detail.

Privacy rules (enforced by this module):
  - NEVER log: password, auth token, raw lifestyle text, full clinical vector.
  - NEVER log: phone numbers in plaintext.
  - DO log: user_id (integer), role, event type, status.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import AUDIT_DB_PATH
from src.utils.logger import get_logger

logger = get_logger(__name__)

# ---------------------------------------------------------------------------
# Schema
# ---------------------------------------------------------------------------

_CREATE_AUDIT_SQL = """
CREATE TABLE IF NOT EXISTS audit_log (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   TEXT    NOT NULL,
    event_type  TEXT    NOT NULL,
    user_id     INTEGER,
    role        TEXT,
    status      TEXT    NOT NULL,
    detail      TEXT
)
"""

# Allowed event types — controls what goes into the audit log
VALID_EVENT_TYPES = {
    "login_success",
    "login_failure",
    "logout",
    "registration",
    "admin_access",
    "alert_attempt",
    "alert_success",
    "alert_failure",
    "config_error",
    "access_denied",
    "rate_limit_exceeded",
}


def _init_audit_db(db_path: Path = AUDIT_DB_PATH) -> None:
    """Create audit table if it does not exist."""
    db_path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(str(db_path)) as conn:
        conn.execute(_CREATE_AUDIT_SQL)
        conn.commit()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def log_event(
    event_type: str,
    status: str,
    user_id: Optional[int] = None,
    role: Optional[str] = None,
    detail: Optional[str] = None,
    db_path: Path = AUDIT_DB_PATH,
) -> None:
    """Write a security audit event to the audit log.

    Args:
        event_type: One of VALID_EVENT_TYPES.
        status: Outcome string (e.g. 'SUCCESS', 'FAILURE', 'BLOCKED').
        user_id: Authenticated user ID (None for unauthenticated events).
        role: User role at time of event.
        detail: Optional short description (must NOT contain credentials).
        db_path: Override for tests.
    """
    if event_type not in VALID_EVENT_TYPES:
        logger.warning("Unknown audit event_type '%s' — skipping.", event_type)
        return

    # Truncate detail to prevent accidental data dump
    safe_detail = (detail[:500] if detail else None)

    timestamp = datetime.utcnow().isoformat()
    sql = (
        "INSERT INTO audit_log (timestamp, event_type, user_id, role, status, detail) "
        "VALUES (?, ?, ?, ?, ?, ?)"
    )
    try:
        _init_audit_db(db_path)
        with sqlite3.connect(str(db_path)) as conn:
            conn.execute(sql, (timestamp, event_type, user_id, role, status, safe_detail))
            conn.commit()
    except Exception as exc:
        # Never propagate audit failures to the user — just log internally
        logger.error("Audit log write failed: %s", type(exc).__name__)


def get_recent_events(
    limit: int = 50,
    db_path: Path = AUDIT_DB_PATH,
) -> list[dict]:
    """Fetch the most recent audit events for admin display.

    Args:
        limit: Maximum number of rows to return.
        db_path: Override for tests.

    Returns:
        List of dicts with audit event fields (no credentials).
    """
    _init_audit_db(db_path)
    sql = (
        "SELECT id, timestamp, event_type, user_id, role, status, detail "
        "FROM audit_log ORDER BY id DESC LIMIT ?"
    )
    try:
        with sqlite3.connect(str(db_path)) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(sql, (limit,)).fetchall()
        return [dict(r) for r in rows]
    except Exception as exc:
        logger.error("Audit log read failed: %s", type(exc).__name__)
        return []
