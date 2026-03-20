"""Command handlers for slash commands.

Each handler is a pure function that takes arguments and returns a text response.
This makes them testable without Telegram.
"""


def handle_start() -> str:
    """Handle /start command — welcome message."""
    return (
        "👋 Welcome to the LMS Bot!\n\n"
        "I can help you check your progress, browse labs, and answer questions.\n\n"
        "Try these commands:\n"
        "/help — See all available commands\n"
        "/health — Check system status\n"
        "/labs — Browse available labs\n"
        "/scores <lab> — Check your scores"
    )


def handle_help() -> str:
    """Handle /help command — list all commands."""
    return (
        "📖 Available Commands:\n\n"
        "/start — Welcome message\n"
        "/help — This help message\n"
        "/health — Check backend status\n"
        "/labs — List available labs\n"
        "/scores <lab> — Get scores for a specific lab\n\n"
        "You can also ask questions in plain language!"
    )


def handle_health() -> str:
    """Handle /health command — check backend status.
    
    TODO: Task 2 — implement actual backend health check.
    For now, returns a placeholder.
    """
    return "🟢 Backend: OK (placeholder — will implement in Task 2)"


def handle_labs() -> str:
    """Handle /labs command — list available labs.
    
    TODO: Task 2 — fetch from backend API.
    For now, returns a placeholder.
    """
    return "📚 Available Labs:\n\n- Lab 1: Introduction\n- Lab 2: Setup\n- Lab 3: Testing\n\n(placeholder — will fetch real data in Task 2)"


def handle_scores(lab: str | None = None) -> str:
    """Handle /scores command — get scores for a lab.
    
    Args:
        lab: Optional lab identifier (e.g., "lab-04")
    
    TODO: Task 2 — fetch from backend API.
    For now, returns a placeholder.
    """
    if lab:
        return f"📊 Scores for {lab}:\n\nTask 1: ✅ Pass\nTask 2: ❌ Fail\n\n(placeholder — will fetch real data in Task 2)"
    return "📊 Scores:\n\nPlease specify a lab, e.g., /scores lab-04\n\n(placeholder — will fetch real data in Task 2)"
