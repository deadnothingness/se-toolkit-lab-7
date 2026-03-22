"""Help command handler."""


def handle_help() -> str:
    """Handle the /help command.

    Returns:
        Help message with available commands.
    """
    return """LMS Bot — Available Commands:

/start — Welcome message
/help — Show this help message
/health — Check system status
/labs — List available labs
/scores <lab> — Get your scores for a lab

You can also ask questions in plain language!"""
