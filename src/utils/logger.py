"""Logging foundation for HeartGuard.

Provides reusable logging that avoids logging sensitive patient information.
"""

import logging
import sys
from typing import Optional


def get_logger(name: str, level: Optional[int] = None) -> logging.Logger:
    """Get a configured logger instance.

    Args:
        name: Logger name, typically __name__.
        level: Logging level. Defaults to INFO.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)

    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    if level is not None:
        logger.setLevel(level)
    elif logger.level == logging.NOTSET:
        logger.setLevel(logging.INFO)

    return logger


def log_info(logger: logging.Logger, message: str) -> None:
    """Log an info message.

    Args:
        logger: Logger instance.
        message: Message to log.
    """
    logger.info(message)


def log_warning(logger: logging.Logger, message: str) -> None:
    """Log a warning message.

    Args:
        logger: Logger instance.
        message: Message to log.
    """
    logger.warning(message)


def log_error(logger: logging.Logger, message: str) -> None:
    """Log an error message.

    Args:
        logger: Logger instance.
        message: Message to log.
    """
    logger.error(message)
