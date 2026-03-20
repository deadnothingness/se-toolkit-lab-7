"""Start command handler.

This is a plain function separated from the Telegram transport layer.
It can be tested directly, called from --test mode, or invoked by Telegram.
"""


def handle_start() -> str:
    """Handle the /start command.

    Returns:
        Welcome message text.
    """
    return "Welcome to the LMS Telegram Bot! Use /help to see available commands."
