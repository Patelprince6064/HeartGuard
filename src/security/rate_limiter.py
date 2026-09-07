"""Session-state rate limiter for HeartGuard login protection (Phase 9).

Limits the number of failed login attempts per Streamlit browser session.
After exceeding the threshold, further attempts are blocked for a cooldown
period.

Streamlit limitations (documented):
  - Rate limiting is per-browser-session (not per IP address or server-wide).
  - Because Streamlit server-side session state is isolated per client,
    an attacker with multiple browser sessions could bypass this limit.
  - For production deployment, use a server-side rate limiter (e.g. nginx
    rate limiting, or a Redis-backed middleware) behind a reverse proxy.
  - This implementation provides a reasonable deterrent for an academic
    demo without introducing external dependencies.
"""

from __future__ import annotations

from datetime import datetime, timedelta

import streamlit as st

from config.settings import LOGIN_COOLDOWN_SECONDS, LOGIN_MAX_ATTEMPTS

# Session state keys
_KEY_ATTEMPTS = "_hg_login_attempts"
_KEY_BLOCKED_UNTIL = "_hg_login_blocked_until"


def _now() -> datetime:
    """Return current UTC datetime."""
    return datetime.utcnow()


def is_rate_limited() -> bool:
    """Check whether the current session is currently rate-limited.

    Returns:
        True if the session should be blocked from further login attempts.
    """
    blocked_until: datetime | None = st.session_state.get(_KEY_BLOCKED_UNTIL)
    if blocked_until is None:
        return False
    if _now() < blocked_until:
        return True
    # Cooldown expired — reset
    st.session_state.pop(_KEY_BLOCKED_UNTIL, None)
    st.session_state[_KEY_ATTEMPTS] = 0
    return False


def record_failed_attempt() -> int:
    """Increment the failed-login counter and apply a block if threshold reached.

    Returns:
        Current attempt count after incrementing.
    """
    current = int(st.session_state.get(_KEY_ATTEMPTS, 0)) + 1
    st.session_state[_KEY_ATTEMPTS] = current

    if current >= LOGIN_MAX_ATTEMPTS:
        blocked_until = _now() + timedelta(seconds=LOGIN_COOLDOWN_SECONDS)
        st.session_state[_KEY_BLOCKED_UNTIL] = blocked_until

    return current


def reset_attempts() -> None:
    """Reset attempt counter on successful login."""
    st.session_state.pop(_KEY_ATTEMPTS, None)
    st.session_state.pop(_KEY_BLOCKED_UNTIL, None)


def seconds_remaining() -> int:
    """Return seconds until the rate-limit block expires (0 if not blocked).

    Returns:
        Integer seconds remaining in the cooldown.
    """
    blocked_until: datetime | None = st.session_state.get(_KEY_BLOCKED_UNTIL)
    if blocked_until is None:
        return 0
    delta = (blocked_until - _now()).total_seconds()
    return max(0, int(delta))
