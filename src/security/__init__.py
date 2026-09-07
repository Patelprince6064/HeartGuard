"""HeartGuard Security Package (Phase 9).

Provides audit logging, input validation, and rate limiting.

Public API:
    - audit_logger: log_event
    - input_validator: validate_email, validate_name, validate_password_strength,
                       validate_lifestyle_text_length, sanitize_text_for_display
    - rate_limiter: check_rate_limit, record_attempt, reset_attempts
"""
