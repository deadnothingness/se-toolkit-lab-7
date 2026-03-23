"""Command handlers for the Telegram bot.

Handlers are plain functions that take input and return text.
They don't know about Telegram — same function works from --test mode,
unit tests, or the actual Telegram bot.
"""

from .commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from .query import handle_query, get_capabilities_hint

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "handle_query",
    "get_capabilities_hint",
]
