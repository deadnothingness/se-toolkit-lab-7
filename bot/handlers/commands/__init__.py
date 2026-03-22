"""Command handlers package."""

from .health import handle_health
from .help import handle_help
from .labs import handle_labs
from .scores import handle_scores
from .start import handle_start

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
]
