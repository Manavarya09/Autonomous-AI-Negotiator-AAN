"""Structured logging with trace IDs for request tracking."""

import logging
import sys
from typing import Optional
from uuid import uuid4
import contextvars

import structlog

_trace_id_var: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("trace_id", default=None)


def get_trace_id() -> Optional[str]:
    """Get current trace ID from context."""
    return _trace_id_var.get()


def set_trace_id(trace_id: Optional[str] = None) -> str:
    """Set trace ID in context."""
    if trace_id is None:
        trace_id = str(uuid4())[:8]
    _trace_id_var.set(trace_id)
    return trace_id


class TraceIdFilter(logging.Filter):
    """Add trace ID to log records."""
    
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = get_trace_id() or "no-trace"
        return True


def configure_logging(level: str = "INFO"):
    """Configure structured logging."""
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )
    
    logging.basicConfig(
        format="%(message)s",
        level=getattr(logging, level.upper()),
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
    )
    
    for handler in logging.root.handlers:
        handler.addFilter(TraceIdFilter())


def log_with_trace(logger: logging.Logger, level: str, message: str, **kwargs):
    """Log with trace ID."""
    trace_id = get_trace_id()
    extra = {"trace_id": trace_id} if trace_id else {}
    extra.update(kwargs)
    
    getattr(logger, level.lower())(message, extra=extra)


def log_info(logger: logging.Logger, message: str, **kwargs):
    """Log info with trace."""
    log_with_trace(logger, "info", message, **kwargs)


def log_error(logger: logging.Logger, message: str, **kwargs):
    """Log error with trace."""
    log_with_trace(logger, "error", message, **kwargs)


def log_warning(logger: logging.Logger, message: str, **kwargs):
    """Log warning with trace."""
    log_with_trace(logger, "warning", message, **kwargs)