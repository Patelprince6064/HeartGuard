"""Session manager for HeartGuard (Phase 9).

Manages authenticated session state inside Streamlit's st.session_state.
Only stores: user_id (int), name (str), role (str).
NEVER stores: password, password_hash, email (beyond display), clinical data.

Streamlit security note:
  Session state is server-side memory per browser session and is not
  transmitted as a cookie. However, there is no cryptographic signing.
  For production deployment, use HTTPS and a reverse proxy.
"""

from __future__ import annotations

from typing import Optional

import streamlit as st

# Session state keys — centralised to prevent typo-based bypass
_KEY_USER_ID = "_hg_user_id"
_KEY_ROLE = "_hg_role"
_KEY_NAME = "_hg_name"
_KEY_IS_AUTH = "_hg_authenticated"

# Keys to purge on logout (all sensitive session keys)
_SENSITIVE_KEYS = [
    _KEY_USER_ID,
    _KEY_ROLE,
    _KEY_NAME,
    _KEY_IS_AUTH,
    # Assessment / patient data
    "assessment_result",
    "lifestyle_result",
    "alert_result",
    "current_patient_data",
]


def create_session(user: dict) -> None:
    """Write authenticated session state from a safe user dict.

    Args:
        user: Safe user dict from auth_service (must contain id, name, role).

    Raises:
        KeyError: If required fields are missing from user dict.
    """
    st.session_state[_KEY_IS_AUTH] = True
    st.session_state[_KEY_USER_ID] = user["id"]
    st.session_state[_KEY_ROLE] = user["role"]
    st.session_state[_KEY_NAME] = user["name"]


def is_authenticated() -> bool:
    """Return True if there is an active authenticated session.

    Returns:
        bool: True if authenticated.
    """
    return bool(st.session_state.get(_KEY_IS_AUTH, False))


def get_current_user() -> Optional[dict]:
    """Return safe user info for the authenticated session.

    Returns:
        Dict with id, name, role — or None if not authenticated.
        Never returns password or password_hash.
    """
    if not is_authenticated():
        return None
    return {
        "id": st.session_state.get(_KEY_USER_ID),
        "name": st.session_state.get(_KEY_NAME, ""),
        "role": st.session_state.get(_KEY_ROLE, ""),
    }


def get_current_user_id() -> Optional[int]:
    """Return the current user's internal ID, or None."""
    return st.session_state.get(_KEY_USER_ID) if is_authenticated() else None


def get_current_role() -> Optional[str]:
    """Return the current user's role string, or None."""
    return st.session_state.get(_KEY_ROLE) if is_authenticated() else None


def clear_session() -> None:
    """Clear all authentication and sensitive session state on logout.

    Removes authentication markers and clears all patient-related temporary
    data to prevent information leakage between sessions.
    """
    for key in _SENSITIVE_KEYS:
        st.session_state.pop(key, None)
