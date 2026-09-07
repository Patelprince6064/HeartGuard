"""Input validation and sanitisation for HeartGuard (Phase 9).

All user-facing inputs pass through these validators before use.
These are distinct from the clinical validators in src/utils/validators.py,
which operate on medical domain values.

Security rules:
  - Reject HTML/script fragments in free-text fields.
  - Enforce length limits everywhere.
  - Validate email format strictly.
  - Never log validated values.
"""

from __future__ import annotations

import html
import re
from typing import Any

from config.settings import (
    EMAIL_MAX_LENGTH,
    LIFESTYLE_TEXT_MAX_LENGTH,
    NAME_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
)

# Simple patterns for dangerous input
_SCRIPT_PATTERN = re.compile(r"<\s*script", re.IGNORECASE)
_HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------


def validate_email(email: Any) -> str:
    """Validate and normalise an email address.

    Args:
        email: Raw email input.

    Returns:
        Normalised lowercase email string.

    Raises:
        ValueError: If the email is invalid or too long.
    """
    if not email:
        raise ValueError("Email address is required.")
    email_str = str(email).strip().lower()
    if len(email_str) > EMAIL_MAX_LENGTH:
        raise ValueError("Email address is too long.")
    if not _EMAIL_RE.match(email_str):
        raise ValueError("Email address format is invalid.")
    return email_str


# ---------------------------------------------------------------------------
# Name
# ---------------------------------------------------------------------------


def validate_name(name: Any) -> str:
    """Validate a display name.

    Args:
        name: Raw name input.

    Returns:
        Cleaned name string.

    Raises:
        ValueError: If empty or too long.
    """
    if not name:
        raise ValueError("Name is required.")
    name_str = str(name).strip()
    if not name_str:
        raise ValueError("Name cannot be blank.")
    if len(name_str) > NAME_MAX_LENGTH:
        raise ValueError(f"Name must be {NAME_MAX_LENGTH} characters or fewer.")
    return name_str


# ---------------------------------------------------------------------------
# Password
# ---------------------------------------------------------------------------


def validate_password_strength(password: str) -> None:
    """Validate password meets minimum requirements.

    Args:
        password: Plaintext password (not logged).

    Raises:
        ValueError: If requirements are not met.
    """
    if not password or len(password) < PASSWORD_MIN_LENGTH:
        raise ValueError(
            f"Password must be at least {PASSWORD_MIN_LENGTH} characters long."
        )


# ---------------------------------------------------------------------------
# Lifestyle text
# ---------------------------------------------------------------------------


def validate_lifestyle_text_length(text: Any) -> str:
    """Validate that lifestyle text is within the allowed length.

    Args:
        text: User-submitted lifestyle description.

    Returns:
        Stripped text string.

    Raises:
        ValueError: If the text exceeds the maximum allowed length.
    """
    if not text:
        raise ValueError("Lifestyle description is required.")
    text_str = str(text).strip()
    if not text_str:
        raise ValueError("Lifestyle description cannot be blank.")
    if len(text_str) > LIFESTYLE_TEXT_MAX_LENGTH:
        raise ValueError(
            f"Lifestyle description is too long. "
            f"Maximum {LIFESTYLE_TEXT_MAX_LENGTH:,} characters allowed."
        )
    return text_str


# ---------------------------------------------------------------------------
# Sanitisation
# ---------------------------------------------------------------------------


def sanitize_text_for_display(text: str) -> str:
    """HTML-escape user-controlled text before rendering in the UI.

    Strips any detected script/HTML fragments and escapes remaining content.

    Args:
        text: User-provided text.

    Returns:
        HTML-escaped string safe for display.
    """
    if not text:
        return ""
    # Remove script tags
    cleaned = _SCRIPT_PATTERN.sub("", text)
    # Remove remaining HTML tags
    cleaned = _HTML_TAG_PATTERN.sub("", cleaned)
    # HTML-escape any residual special characters
    return html.escape(cleaned)


def sanitize_sms_content(value: str) -> str:
    """Sanitise a dynamic value before inclusion in an SMS message.

    Removes newlines and pipe characters that could be used for
    SMS message injection.

    Args:
        value: Dynamic string value to include in SMS.

    Returns:
        Sanitised string.
    """
    if not value:
        return ""
    # Strip newlines and pipes that could create false SMS structure
    return re.sub(r"[\r\n|]", " ", str(value)).strip()
