"""Authentication service for HeartGuard (Phase 9).

Orchestrates user registration and login. Applies input validation,
password hashing, and safe error responses. Never reveals whether a
specific email exists on failed login.

Public API:
    register_user(name, email, password, confirm_password) -> dict
    authenticate_user(email, password) -> dict | None
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Optional

from config.settings import (
    AUTH_DB_PATH,
    EMAIL_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    ROLE_PATIENT,
)
from src.auth.models import init_auth_db
from src.auth.password_service import hash_password, verify_password
from src.auth.user_repository import create_user, find_by_email
from src.utils.logger import get_logger

logger = get_logger(__name__)

# Simple RFC-5322-like email regex (strict enough for registration)
_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _normalise_email(email: str) -> str:
    """Lowercase and strip whitespace from email for consistent storage."""
    return email.strip().lower()


def _validate_email_format(email: str) -> None:
    """Raise ValueError if email format is invalid."""
    if not email or len(email) > EMAIL_MAX_LENGTH:
        raise ValueError("Email address is invalid.")
    if not _EMAIL_RE.match(email):
        raise ValueError("Email address is invalid.")


def _validate_name(name: str) -> None:
    """Raise ValueError if name is empty or too long."""
    if not name or not name.strip():
        raise ValueError("Name is required.")
    if len(name.strip()) > NAME_MAX_LENGTH:
        raise ValueError(f"Name must be {NAME_MAX_LENGTH} characters or fewer.")


def _validate_password(password: str) -> None:
    """Raise ValueError if password does not meet requirements."""
    if not password or len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters long."
        )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def register_user(
    name: str,
    email: str,
    password: str,
    confirm_password: str,
    db_path: Path = AUTH_DB_PATH,
) -> dict:
    """Register a new PATIENT user account.

    Role is always set to PATIENT on self-registration.
    Admin accounts must be created via scripts/create_admin.py.

    Args:
        name: Display name.
        email: Email address (will be normalised to lowercase).
        password: Plaintext password (hashed immediately, never stored).
        confirm_password: Must match password.
        db_path: Override for tests.

    Returns:
        Safe user dict (no password_hash).

    Raises:
        ValueError: On any validation failure or duplicate email.
    """
    # Validate name
    _validate_name(name)
    clean_name = name.strip()

    # Validate and normalise email
    _validate_email_format(email)
    clean_email = _normalise_email(email)

    # Validate password
    _validate_password(password)

    # Confirm passwords match (never log either value)
    if password != confirm_password:
        raise ValueError("Passwords do not match.")

    # Ensure DB is ready
    init_auth_db(db_path)

    # Hash immediately — plaintext never persisted
    pw_hash = hash_password(password)

    # create_user raises ValueError on duplicate email
    user = create_user(
        name=clean_name,
        email=clean_email,
        password_hash=pw_hash,
        role=ROLE_PATIENT,
        db_path=db_path,
    )

    logger.info("Registration successful: user_id=%s role=%s", user.id, user.role)
    return user.to_safe_dict()


def authenticate_user(
    email: str,
    password: str,
    db_path: Path = AUTH_DB_PATH,
) -> Optional[dict]:
    """Authenticate a user by email and password.

    Intentionally generic error path — does NOT reveal whether an email
    exists in the database.

    Args:
        email: Email provided at login.
        password: Plaintext password provided at login.
        db_path: Override for tests.

    Returns:
        Safe user dict on success, None on failure.
    """
    if not email or not password:
        return None

    clean_email = _normalise_email(email)

    # Retrieve user — even if not found, we run verify_password against a
    # dummy hash to prevent timing-based email enumeration.
    user = find_by_email(clean_email, db_path=db_path)

    if user is None:
        # Run a dummy verification to normalise timing
        verify_password(password, "$2b$12$invalidhashplaceholder00000000000000000000000000000000")
        logger.warning("Login attempt for unknown email (redacted)")
        return None

    if not user.is_active:
        verify_password(password, "$2b$12$invalidhashplaceholder00000000000000000000000000000000")
        logger.warning("Login attempt for deactivated account: user_id=%s", user.id)
        return None

    if not verify_password(password, user.password_hash):
        logger.warning("Failed login: user_id=%s", user.id)
        return None

    logger.info("Login successful: user_id=%s role=%s", user.id, user.role)
    return user.to_safe_dict()


def create_admin_user(
    name: str,
    email: str,
    password: str,
    db_path: Path = AUTH_DB_PATH,
) -> dict:
    """Create an ADMIN user account.

    This function is called only by scripts/create_admin.py, which reads
    credentials from environment variables. Never called from the UI.

    Args:
        name: Admin display name.
        email: Admin email.
        password: Plaintext password (hashed immediately).
        db_path: Override for tests.

    Returns:
        Safe user dict.

    Raises:
        ValueError: On validation failure or duplicate email.
    """
    _validate_name(name)
    _validate_email_format(email)
    _validate_password(password)

    clean_email = _normalise_email(email)
    pw_hash = hash_password(password)

    init_auth_db(db_path)
    user = create_user(
        name=name.strip(),
        email=clean_email,
        password_hash=pw_hash,
        role="ADMIN",
        db_path=db_path,
    )
    logger.info("Admin account created: user_id=%s", user.id)
    return user.to_safe_dict()
