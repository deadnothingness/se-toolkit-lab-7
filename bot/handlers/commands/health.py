"""Health check command handler."""

import httpx
from services.api_client import create_client


def handle_health(lms_api_url: str, lms_api_key: str) -> str:
    """Handle the /health command.

    Args:
        lms_api_url: LMS backend URL from config.
        lms_api_key: LMS API key from config.

    Returns:
        System health status message.
    """
    try:
        with create_client(lms_api_url, lms_api_key) as client:
            result = client.health_check()
            return f"✅ Backend is healthy. {result['item_count']} items available."
    except httpx.ConnectError as e:
        # Connection refused, DNS failure, etc.
        error_detail = str(e.args[0]) if e.args else "connection error"
        return f"❌ Backend error: {error_detail} ({lms_api_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        # HTTP error status (4xx, 5xx)
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.TimeoutException:
        return f"❌ Backend error: request timed out ({lms_api_url}). The service may be overloaded."
    except Exception as e:
        # Catch-all for unexpected errors, but still show the error
        error_type = type(e).__name__
        return f"❌ Backend error: {error_type} - {e!s}"
