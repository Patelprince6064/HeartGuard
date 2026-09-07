"""User repository for HeartGuard authentication (Phase 9).

Data-access layer for the users table. All queries use parameterized
statements — no string concatenation with user input is ever performed.

Never returns password_hash outside this module; callers receive User
objects and must call User.to_safe_dict() for UI consumption.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from config.settings import AUTH_DB_PATH
from src.auth.models import User, init_auth_db
from src.utils.logger import get_logger

logger = get_logger(__name__)


def _get_connection(db_path: Path = AUTH_DB_PATH) -> sqlite3.Connection:
    """Return a thread-safe SQLite connection with row factory set."""
    init_auth_db(db_path)
    conn = sqlite3.connect(str(db_path), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def _row_to_user(row: sqlite3.Row) -> User:
    """Convert a sqlite3.Row to a User dataclass."""
    return User(
        id=row["id"],
        name=row["name"],
        email=row["email"],
        password_hash=row["password_hash"],
        role=row["role"],
        is_active=bool(row["is_active"]),
        created_at=row["created_at"],
        updated_at=row["updated_at"],
    )


# ---------------------------------------------------------------------------
# Write operations
# ---------------------------------------------------------------------------


def create_user(
    name: str,
    email: str,
    password_hash: str,
    role: str = "PATIENT",
    db_path: Path = AUTH_DB_PATH,
) -> User:
    """Insert a new user record.

    Args:
        name: Display name.
        email: Normalised lowercase email.
        password_hash: bcrypt hash (never plaintext).
        role: 'PATIENT' or 'ADMIN'.
        db_path: Override DB path (used in tests).

    Returns:
        Newly created User with populated id.

    Raises:
        ValueError: If email already exists.
    """
    now = datetime.utcnow().isoformat()
    sql = (
        "INSERT INTO users (name, email, password_hash, role, is_active, created_at, updated_at) "
        "VALUES (?, ?, ?, ?, 1, ?, ?)"
    )
    try:
        with _get_connection(db_path) as conn:
            cursor = conn.execute(sql, (name, email, password_hash, role, now, now))
            conn.commit()
            user_id = cursor.lastrowid
    except sqlite3.IntegrityError:
        raise ValueError(f"Email address is already registered.")

    logger.info("User created: id=%s role=%s", user_id, role)
    return User(
        id=user_id,
        name=name,
        email=email,
        password_hash=password_hash,
        role=role,
        is_active=True,
        created_at=now,
        updated_at=now,
    )


def deactivate_user(user_id: int, db_path: Path = AUTH_DB_PATH) -> bool:
    """Deactivate a user account (soft delete).

    Args:
        user_id: ID of the account to deactivate.
        db_path: Override DB path (used in tests).

    Returns:
        True if a row was updated, False if not found.
    """
    now = datetime.utcnow().isoformat()
    sql = "UPDATE users SET is_active=0, updated_at=? WHERE id=?"
    with _get_connection(db_path) as conn:
        cursor = conn.execute(sql, (now, user_id))
        conn.commit()
    updated = cursor.rowcount > 0
    if updated:
        logger.info("User deactivated: id=%s", user_id)
    return updated


# ---------------------------------------------------------------------------
# Read operations
# ---------------------------------------------------------------------------


def find_by_email(email: str, db_path: Path = AUTH_DB_PATH) -> Optional[User]:
    """Find an active user by normalised lowercase email.

    Args:
        email: Normalised email to look up.
        db_path: Override DB path (used in tests).

    Returns:
        User if found and active, None otherwise.
    """
    sql = "SELECT * FROM users WHERE email=? AND is_active=1 LIMIT 1"
    with _get_connection(db_path) as conn:
        row = conn.execute(sql, (email,)).fetchone()
    return _row_to_user(row) if row else None


def find_by_id(user_id: int, db_path: Path = AUTH_DB_PATH) -> Optional[User]:
    """Find a user by primary key.

    Args:
        user_id: Internal user ID.
        db_path: Override DB path (used in tests).

    Returns:
        User if found, None otherwise.
    """
    sql = "SELECT * FROM users WHERE id=? LIMIT 1"
    with _get_connection(db_path) as conn:
        row = conn.execute(sql, (user_id,)).fetchone()
    return _row_to_user(row) if row else None


def list_users(db_path: Path = AUTH_DB_PATH) -> List[User]:
    """List all user accounts (admin view).

    Returns only safe fields — password_hash is included in the User
    object but callers must use to_safe_dict() before displaying.

    Args:
        db_path: Override DB path (used in tests).

    Returns:
        List of User objects.
    """
    sql = "SELECT * FROM users ORDER BY created_at DESC"
    with _get_connection(db_path) as conn:
        rows = conn.execute(sql).fetchall()
    return [_row_to_user(r) for r in rows]


def count_users_by_role(db_path: Path = AUTH_DB_PATH) -> dict:
    """Return user counts grouped by role.

    Args:
        db_path: Override DB path (used in tests).

    Returns:
        Dict mapping role name to count.
    """
    sql = "SELECT role, COUNT(*) as cnt FROM users WHERE is_active=1 GROUP BY role"
    with _get_connection(db_path) as conn:
        rows = conn.execute(sql).fetchall()
    return {row["role"]: row["cnt"] for row in rows}
