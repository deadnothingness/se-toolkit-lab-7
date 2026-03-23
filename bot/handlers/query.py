"""Natural language query handler using LLM intent routing."""

import sys

import httpx

from services.api_client import create_client
from services.llm_client import create_llm_client, get_tool_definitions
from handlers.intent_router import route, is_greeting_or_gibberish


def handle_query(
    message: str,
    lms_api_url: str,
    lms_api_key: str,
    llm_api_base_url: str,
    llm_api_key: str,
    llm_api_model: str,
    debug: bool = True,
) -> str:
    """Handle a natural language query using LLM intent routing.

    Args:
        message: The user's message.
        lms_api_url: LMS backend URL.
        lms_api_key: LMS API key.
        llm_api_base_url: LLM API base URL.
        llm_api_key: LLM API key.
        llm_api_model: LLM model name.
        debug: If True, print debug info to stderr.

    Returns:
        Response text.
    """

    def log(msg: str) -> None:
        """Print debug message to stderr if debug mode is on."""
        if debug:
            print(msg, file=sys.stderr)

    # Check for simple greetings or gibberish first
    is_simple, simple_response = is_greeting_or_gibberish(message)
    if is_simple and simple_response:
        log(f"[precheck] Handled as greeting/gibberish")
        return simple_response

    # Check if LLM is configured
    if not llm_api_key or not llm_api_key.strip():
        log("[precheck] LLM not configured, returning helpful message")
        return (
            "I can answer questions about labs, scores, and student performance, "
            "but the LLM service isn't configured yet. Try using slash commands like "
            "/health, /labs, or /scores for now."
        )

    try:
        # Create clients and route the query
        with create_client(lms_api_url, lms_api_key) as lms_client, create_llm_client(
            llm_api_base_url, llm_api_key, llm_api_model
        ) as llm_client:
            response = route(message, lms_client, llm_client, debug=debug)
            return response

    except httpx.ConnectError as e:
        error_detail = str(e.args[0]) if e.args else "connection error"
        log(f"[error] LLM connection error: {error_detail}")
        return f"❌ LLM error: {error_detail}. The LLM service may be down."
    except httpx.HTTPStatusError as e:
        log(f"[error] LLM HTTP error: {e.response.status_code}")
        if e.response.status_code == 401:
            return (
                "❌ LLM error: Authentication failed (HTTP 401). "
                "The API token may have expired. Try restarting the Qwen proxy: "
                "cd ~/qwen-code-oai-proxy && docker compose restart"
            )
        return f"❌ LLM error: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except httpx.TimeoutException:
        log("[error] LLM timeout")
        return "❌ LLM error: request timed out. The service may be overloaded."
    except Exception as e:
        error_type = type(e).__name__
        log(f"[error] Unexpected error: {error_type} - {e}")
        return f"❌ LLM error: {error_type} - {e!s}"


def get_capabilities_hint() -> str:
    """Get a hint about what the bot can do.

    Returns:
        String describing bot capabilities.
    """
    return (
        "I can help you with:\n\n"
        "• Listing available labs\n"
        "• Showing scores and pass rates for a lab\n"
        "• Finding top learners\n"
        "• Comparing group performance\n"
        "• Viewing submission timelines\n"
        "• Checking completion rates\n\n"
        "Try asking: 'which lab has the lowest pass rate?' or 'show me top 5 students in lab 4'"
    )
