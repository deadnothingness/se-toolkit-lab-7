"""Telegram bot entry point.

Supports two modes:
1. --test mode: Call handlers directly for offline testing
2. Normal mode: Run the Telegram bot using python-telegram-bot

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

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

from handlers.commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from handlers.query import handle_query
from config import load_config


def parse_command(text: str) -> tuple[str, str | None]:
    """Parse a command string into command and argument."""
    parts = text.strip().split(maxsplit=1)
    command = parts[0].lower()
    argument = parts[1] if len(parts) > 1 else None
    return command, argument


def is_natural_language_query(text: str) -> bool:
    """Check if input is a natural language query (not a slash command)."""
    text = text.strip()
    return not text.startswith("/")


def get_inline_keyboard() -> InlineKeyboardMarkup:
    """Get inline keyboard buttons for common queries."""
    keyboard = [
        [
            InlineKeyboardButton("📊 Health", callback_data="health"),
            InlineKeyboardButton("📚 Labs", callback_data="labs"),
        ],
        [
            InlineKeyboardButton("🏆 Top Students", callback_data="top_5"),
            InlineKeyboardButton("📈 Pass Rates", callback_data="pass_rates"),
        ],
        [
            InlineKeyboardButton("❓ Lowest Pass Rate", callback_data="lowest_pass"),
            InlineKeyboardButton("👥 Groups", callback_data="groups"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def format_keyboard_hint() -> str:
    """Format a hint about inline keyboard buttons."""
    return (
        "\n\n💡 Quick actions:\n"
        "Tap the buttons below to quickly check health, labs, top students, and more!"
    )


async def cmd_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command."""
    response = handle_start() + format_keyboard_hint()
    await update.message.reply_text(response, reply_markup=get_inline_keyboard())


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command."""
    response = handle_help()
    await update.message.reply_text(response)


async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /health command."""
    config = load_config()
    response = handle_health(
        lms_api_url=config["LMS_API_URL"],
        lms_api_key=config["LMS_API_KEY"],
    )
    await update.message.reply_text(response)


async def cmd_labs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /labs command."""
    config = load_config()
    response = handle_labs(
        lms_api_url=config["LMS_API_URL"],
        lms_api_key=config["LMS_API_KEY"],
    )
    await update.message.reply_text(response)


async def cmd_scores(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /scores command."""
    config = load_config()
    arg = context.args[0] if context.args else None
    response = handle_scores(
        lab_name=arg,
        lms_api_url=config["LMS_API_URL"],
        lms_api_key=config["LMS_API_KEY"],
    )
    await update.message.reply_text(response)


async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button presses."""
    query = update.callback_query
    await query.answer()
    
    config = load_config()
    callback_data = query.data
    
    if callback_data == "health":
        response = handle_health(
            lms_api_url=config["LMS_API_URL"],
            lms_api_key=config["LMS_API_KEY"],
        )
    elif callback_data == "labs":
        response = handle_labs(
            lms_api_url=config["LMS_API_URL"],
            lms_api_key=config["LMS_API_KEY"],
        )
    elif callback_data == "top_5":
        response = handle_query(
            message="show top 5 students",
            lms_api_url=config["LMS_API_URL"],
            lms_api_key=config["LMS_API_KEY"],
            llm_api_base_url=config["LLM_API_BASE_URL"],
            llm_api_key=config["LLM_API_KEY"],
            llm_api_model=config["LLM_API_MODEL"],
            debug=False,
        )
    elif callback_data == "pass_rates":
        response = handle_query(
            message="show pass rates for all labs",
            lms_api_url=config["LMS_API_URL"],
            lms_api_key=config["LMS_API_KEY"],
            llm_api_base_url=config["LLM_API_BASE_URL"],
            llm_api_key=config["LLM_API_KEY"],
            llm_api_model=config["LLM_API_MODEL"],
            debug=False,
        )
    elif callback_data == "lowest_pass":
        response = handle_query(
            message="which lab has the lowest pass rate",
            lms_api_url=config["LMS_API_URL"],
            lms_api_key=config["LMS_API_KEY"],
            llm_api_base_url=config["LLM_API_BASE_URL"],
            llm_api_key=config["LLM_API_KEY"],
            llm_api_model=config["LLM_API_MODEL"],
            debug=False,
        )
    elif callback_data == "groups":
        response = handle_query(
            message="show group performance",
            lms_api_url=config["LMS_API_URL"],
            lms_api_key=config["LMS_API_KEY"],
            llm_api_base_url=config["LLM_API_BASE_URL"],
            llm_api_key=config["LLM_API_KEY"],
            llm_api_model=config["LLM_API_MODEL"],
            debug=False,
        )
    else:
        response = "Unknown action."
    
    await query.edit_message_text(response)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle natural language messages."""
    text = update.message.text
    if not text:
        return
    
    config = load_config()
    
    response = handle_query(
        message=text,
        lms_api_url=config["LMS_API_URL"],
        lms_api_key=config["LMS_API_KEY"],
        llm_api_base_url=config["LLM_API_BASE_URL"],
        llm_api_key=config["LLM_API_KEY"],
        llm_api_model=config["LLM_API_MODEL"],
        debug=False,
    )
    await update.message.reply_text(response)


def run_test_mode(command_text: str) -> None:
    """Run a command in test mode and print the result."""
    config = load_config()

    if is_natural_language_query(command_text):
        response = handle_query(
            message=command_text,
            lms_api_url=config["LMS_API_URL"],
            lms_api_key=config["LMS_API_KEY"],
            llm_api_base_url=config["LLM_API_BASE_URL"],
            llm_api_key=config["LLM_API_KEY"],
            llm_api_model=config["LLM_API_MODEL"],
            debug=True,
        )
        print(response)
        return

    command, arg = parse_command(command_text)

    if command == "/start":
        response = handle_start() + format_keyboard_hint()
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

    print(response)


def run_telegram_bot() -> None:
    """Run the Telegram bot using python-telegram-bot with polling."""
    config = load_config()

    if not config["BOT_TOKEN"]:
        print("Error: BOT_TOKEN not found in .env.bot.secret")
        print("Please copy .env.bot.example to .env.bot.secret and fill in your bot token.")
        sys.exit(1)

    print("Starting Telegram bot...")
    print(f"Bot token configured: {'Yes' if config['BOT_TOKEN'] else 'No'}")
    print(f"LMS API URL: {config['LMS_API_URL']}")
    print(f"LLM API Base: {config['LLM_API_BASE_URL']}")
    print()
    print("Bot is running. Press Ctrl+C to stop.")

    # Build the application
    app = Application.builder().token(config["BOT_TOKEN"]).build()

    # Add command handlers
    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("help", cmd_help))
    app.add_handler(CommandHandler("health", cmd_health))
    app.add_handler(CommandHandler("labs", cmd_labs))
    app.add_handler(CommandHandler("scores", cmd_scores))

    # Add callback query handler for inline keyboard
    app.add_handler(CallbackQueryHandler(handle_callback))

    # Add message handler for natural language queries (non-command messages)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Start polling - this runs forever until interrupted
    app.run_polling(allowed_updates=Update.ALL_TYPES)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="LMS Telegram Bot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    uv run bot.py --test "/start"      # Test /start command
    uv run bot.py --test "/help"       # Test /help command
    uv run bot.py --test "what labs are available"  # Natural language query
    uv run bot.py                      # Run the Telegram bot
        """,
    )
    parser.add_argument(
        "--test",
        metavar="QUERY",
        help="Run a command or query in test mode (no Telegram connection)",
    )

    args = parser.parse_args()

    if args.test:
        run_test_mode(args.test)
    else:
        run_telegram_bot()


if __name__ == "__main__":
    main()
