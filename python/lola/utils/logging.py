# Standard imports
import os
import logging
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

# Third-party imports
from logging.handlers import RotatingFileHandler

"""
File: Defines logging setup for LOLA OS with structured JSON output and rotation.

Purpose: Provides consistent, production-ready logging across components, masking secrets and enabling telemetry.
How: Configures root logger with JSON formatter, console/file handlers (10MB rotation, 5 backups), and extra fields.
Why: Ensures observability without vendor lock-in, aligned to LOLA's developer sovereignty from V1.
Full Path: lola-os/python/lola/utils/logging.py
"""

_STANDARD_KEYS = {
    'name', 'msg', 'args', 'levelname', 'levelno', 'pathname', 'filename', 'module',
    'exc_info', 'exc_text', 'stack_info', 'lineno', 'funcName', 'created', 'msecs',
    'relativeCreated', 'thread', 'threadName', 'processName', 'process', 'message'
}

class JSONFormatter(logging.Formatter):
    """JSONFormatter: Custom formatter for structured logs. Does NOT handle non-dict extras."""

    def format(self, record: logging.LogRecord) -> str:
        # Inline: Extract extras from record.__dict__ (logging flattens extra kwarg)
        extra = {k: v for k, v in record.__dict__.items() if k not in _STANDARD_KEYS}
        extra.setdefault("process_id", os.getpid())
        log_entry: Dict[str, Any] = {
            "timestamp": datetime.fromtimestamp(record.created).isoformat(),
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "extra": extra,
        }
        if record.exc_info:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)

def setup_logger(name: str = "lola", log_file: str = "lola.log", level: str = "INFO") -> logging.Logger:
    """
    Sets up a structured logger for LOLA OS.

    Args:
        name: Logger name (default: "lola").
        log_file: Path to log file (default: "lola.log").
        level: Logging level (default: "INFO").

    Returns:
        Configured logger instance.

    Does Not: Configure external handlers—focus on LOLA root.
    """
    # Inline: Remove existing handlers to avoid duplicates
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level.upper()))

    # Inline: Console handler with JSON
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(JSONFormatter())
    logger.addHandler(console_handler)

    # Inline: File handler with rotation (10MB, 5 backups)
    file_handler = RotatingFileHandler(
        Path(log_file), maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
    )
    file_handler.setFormatter(JSONFormatter())
    logger.addHandler(file_handler)

    return logger

__all__ = ["setup_logger", "JSONFormatter"]