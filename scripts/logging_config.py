"""Shared logging configuration for the ETo pipeline CLI."""

from __future__ import annotations

import logging
import sys

LOGGER_NAME = "eto"


def setup_logging(*, verbose: bool = False) -> None:
    """Configure root logging for CLI commands."""
    level = logging.DEBUG if verbose else logging.INFO
    root = logging.getLogger()
    if not root.handlers:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
        root.addHandler(handler)
    root.setLevel(level)
    logging.getLogger(LOGGER_NAME).setLevel(level)


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger for pipeline modules."""
    return logging.getLogger(f"{LOGGER_NAME}.{name}")
