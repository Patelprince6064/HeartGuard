# HeartGuard Security & Production Hardening (Phase 9)

## 1. Overview & Threat Model

HeartGuard is an AI-assisted clinical decision support system designed for cardiovascular risk stratification and explainability. Given the sensitivity of medical assessments and patient contact details, Phase 9 establishes a defense-in-depth security framework covering authentication, role-based access control (RBAC), data sanitization, privacy preservation, audit logging, and alert dispatch integrity.

### Threat Model Matrix

| Threat / Vector | Potential Impact | HeartGuard Mitigation |
| :--- | :--- | :--- |
| **Credential Theft / Brute Force** | Unauthorized account access | Bcrypt with 12 rounds, constant-time verification, session-level rate limiting (5 attempts, 60s lockout), generic login failure responses. |
| **Privilege Escalation** | Patient viewing admin analytics or model internals | Strict RBAC guards (`require_role("ADMIN")`), admin creation restricted to out-of-band CLI tool reading environment variables. |
| **Injection Attacks (SQLi, XSS)** | Database corruption or script execution in browser | Parameterized SQLite queries (`?` bindings), HTML escaping, regex-based `<script>` tag stripping, length bounds. |
| **Patient Privacy Leakage** | Exposure of PII, clinical metrics, or lifestyle disclosures | Phone number masking (`+1*****4567`), lifestyle text strictly excluded from logs and SMS payloads, password hashes stripped from user dictionaries. |
| **Alert Forgery / SMS Spam** | Unauthorized Twilio dispatches or alert flooding | Strict threshold triage (> 85%), cryptographic assessment IDs, idempotent deduplication (`is_alert_already_sent`), demo mode safe fallback. |

---

## 2. Authentication & Role-Based Access Control (RBAC)

### User Roles
1. **`PATIENT`**:
   - Access to personal risk assessments, lifestyle analysis, and self-service recommendations.
   - Strictly prohibited from viewing system administration, audit logs, or global model explainability diagnostics.
2. **`ADMIN`**:
   - Access to clinician audit trails, system health, user management, and advanced model explainability dashboards (`explainable_ai.py`, `model_performance.py`).

### Registration & Credential Provisioning
- **Self-Service Registration:** Only `PATIENT` role accounts may be created via the registration portal (`pages/register.py`).
- **Administrative Accounts:** Admin accounts cannot be created through the web interface. They must be provisioned via the secure CLI utility:
  ```powershell
  python scripts/create_admin.py
  ```
  This utility reads credentials strictly from `ADMIN_EMAIL` and `ADMIN_PASSWORD` environment variables and validates password strength before committing to the database.

---

## 3. Password Storage & Cryptographic Standards

- **Hashing Algorithm:** Bcrypt (`bcrypt>=4.0.0`) with a work factor of **12 salt rounds**.
- **Timing Attack Mitigation:** Authentication verifies passwords using bcrypt's constant-time comparison. In scenarios where a requested user does not exist, a dummy bcrypt verification is executed to prevent user enumeration via timing discrepancies.
- **Serialization Safety:** The `User` domain model provides `to_safe_dict()`, ensuring `password_hash` is never serialized to UI states or JSON representations.

---

## 4. Input Validation & Data Sanitization

All incoming parameters are validated and sanitized in `src/security/input_validator.py` prior to processing:

- **Email Validation:** Validated against RFC-compliant regex and bounded to 255 characters.
- **Name Sanitization:** Cleaned and bounded to 100 characters.
- **Password Complexity:** Enforces a minimum of 8 characters.
- **Lifestyle Narrative Bounds:** Validated up to 5,000 characters to prevent buffer saturation or resource exhaustion.
- **XSS Mitigation:** `sanitize_text_for_display` removes `<script>` blocks, strips lingering HTML tags, and applies HTML entity encoding.
- **SMS Content Protection:** `sanitize_sms_content` strips carriage returns, newlines, and pipe characters (`\r`, `\n`, `|`) to avoid SMS spoofing or formatting manipulation.

---

## 5. Patient Data Protection & Privacy

1. **Phone Number Masking:**
   - Clinician and emergency contact numbers are masked across all UI surfaces, database records, and logs (e.g. `+1*****4567`).
2. **Lifestyle Text Confidentiality:**
   - Free-form text submitted to the NLP analyzer is processed in memory and never logged to persistent audit logs, console outputs, or SMS messages.
3. **Clinical Vector Isolation:**
   - Raw clinical physiological arrays are omitted from general application logs.

---

## 6. Audit Logging Architecture

Security-relevant events are written to an isolated SQLite audit store (`data/security/audit.db`):

- **Whitelisted Event Types:**
  - `login_success`, `login_failure`, `logout`
  - `registration`
  - `admin_access`, `access_denied`
  - `alert_attempt`, `alert_success`, `alert_failure`
  - `rate_limit_exceeded`, `config_error`
- **Tamper & Overflow Resistance:**
  - Event details are truncated to 500 characters.
  - Logging operations fail gracefully without exposing database errors to end users.

---

## 7. Emergency Alert Security & Idempotency

1. **Threshold Enforcement:**
   - Emergency dispatch is triggered strictly when overall risk > 85.0%. Scores $\le 85.0\%$ terminate the workflow with `NOT_TRIGGERED`.
2. **Idempotency & Deduplication:**
   - Every risk calculation generates or accepts a unique `assessment_id`.
   - `AlertManager` checks `is_alert_already_sent(assessment_id, recipient)` before contacting Twilio. Subsequent triggers return an `already_sent` status without duplicate SMS dispatch.
3. **Demo Mode Safety:**
   - When `ALERTS_ENABLED=false` or Twilio credentials are unconfigured, alerts are simulated and logged as `DISABLED` in the audit database, preventing unintended external communications.

---

## 8. Production Hardening Checklist

- [x] Passwords hashed with bcrypt (work factor 12)
- [x] Generic error messages for failed logins ("Invalid email or password.")
- [x] Rate limiting on login attempts
- [x] Strict RBAC guards on administrative and diagnostic pages
- [x] Parameterized SQL queries preventing SQL injection
- [x] Input sanitization against XSS and SMS injection
- [x] PII masking (phone numbers) in logs and UI
- [x] Lifestyle narrative shielded from persistent logs
- [x] Idempotent alert dispatch preventing duplicate SMS alerts
- [x] Secret management via environment variables (`.env`) with `.env.example` templates
- [x] SQLite databases excluded from version control (`.gitignore`)
