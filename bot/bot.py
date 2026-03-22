"""Telegram bot entry point.

Supports two modes:
1. --test mode: Call handlers directly for offline testing
2. Normal mode: Run the Telegram bot

Usage:
    uv run bot.py --test "/start"    # Test mode
    uv run bot.py                    # Run Telegram bot
"""

import argparse
import sys
from pathlib import Path

# Add bot directory to path for imports
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from handlers.commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from config import load_config


def parse_command(text: str) -> tuple[str, str | None]:
    """Parse a command string into command and argument.
    
    Args:
        text: The command text, e.g., "/start" or "/scores lab-04"
    
    Returns:
        Tuple of (command, argument) where argument may be None.
    """
    parts = text.strip().split(maxsplit=1)
    command = parts[0].lower()
    argument = parts[1] if len(parts) > 1 else None
    return command, argument


def run_test_mode(command_text: str) -> None:
    """Run a command in test mode and print the result.

    Args:
        command_text: The command to test, e.g., "/start" or "/scores lab-04"
    """
    command, arg = parse_command(command_text)

    # Load config for handlers that need backend access
    config = load_config()

    # Route to the appropriate handler
    if command == "/start":
        response = handle_start()
    elif command == "/help":
        response = handle_help()
    elif command == "/health":
        response = handle_health(
            lms_api_url=config["LMS_API_URL"],
            lms_api_key=config["LMS_API_KEY"],
        )
    elif command == "/labs":
        response = handle_labs(
            lms_api_url=config["LMS_API_URL"],
            lms_api_key=config["LMS_API_KEY"],
        )
    elif command == "/scores":
        response = handle_scores(
            lab_name=arg,
            lms_api_url=config["LMS_API_URL"],
            lms_api_key=config["LMS_API_KEY"],
        )
    else:
        response = f"❓ Unknown command: {command}\n\nUse /help to see available commands."

    # Print response to stdout
    print(response)


def run_telegram_bot() -> None:
    """Run the Telegram bot.
    
    TODO: Task 2 — implement Telegram bot using aiogram.
    For now, this is a placeholder.
    """
    config = load_config()
    
    if not config["BOT_TOKEN"]:
        print("Error: BOT_TOKEN not found in .env.bot.secret")
        print("Please copy .env.bot.example to .env.bot.secret and fill in your bot token.")
        sys.exit(1)
    
    print("Starting Telegram bot...")
    print(f"Bot token configured: {'Yes' if config['BOT_TOKEN'] else 'No'}")
    print(f"LMS API URL: {config['LMS_API_URL']}")
    print()
    print("TODO: Task 2 — implement Telegram bot using aiogram")
    print("For now, the bot is running but not processing messages.")


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LMS Telegram Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run bot.py --test "/start"      # Test /start command
    uv run bot.py --test "/help"       # Test /help command
    uv run bot.py                      # Run the Telegram bot
        """,
    )
    parser.add_argument(
        "--test",
        metavar="COMMAND",
        help="Run a command in test mode (no Telegram connection)",
    )
    
    args = parser.parse_args()
    
    if args.test:
        # Test mode: call handlers directly
        run_test_mode(args.test)
    else:
        # Normal mode: run Telegram bot
        run_telegram_bot()


if __name__ == "__main__":
    main()
