"""Scores command handler."""

import httpx
from services.api_client import create_client


def handle_scores(lab_name: str | None, lms_api_url: str, lms_api_key: str) -> str:
    """Handle the /scores command.

    Args:
        lab_name: Lab identifier to fetch scores for.
        lms_api_url: LMS backend URL from config.
        lms_api_key: LMS API key from config.

    Returns:
        Scores information for the specified lab.
    """
    if not lab_name:
        return "📊 Usage: /scores <lab_name>\n\nExample: /scores lab-04"

    try:
        with create_client(lms_api_url, lms_api_key) as client:
            pass_rates = client.get_pass_rates(lab_name)

            if not pass_rates:
                return f"📊 No scores found for '{lab_name}'. Check the lab identifier."

            # Format pass rates
            lines = [f"📊 Pass rates for {lab_name}:"]
            for rate in pass_rates:
                task_name = rate.get("task", rate.get("task_name", "Unknown"))
                # API returns avg_score as percentage (0-100), not pass_rate as fraction
                pass_rate = rate.get("pass_rate", rate.get("avg_score", rate.get("average", 0)))
                attempts = rate.get("attempts", rate.get("count", 0))

                # Format percentage (API already returns 0-100 scale)
                percentage = f"{pass_rate:.1f}%"

                lines.append(f"- {task_name}: {percentage} ({attempts} attempts)")

            return "\n".join(lines)

    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"📊 Lab '{lab_name}' not found. Use /labs to see available labs."
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}."
    except httpx.ConnectError as e:
        error_detail = str(e.args[0]) if e.args else "connection error"
        return f"❌ Backend error: {error_detail} ({lms_api_url}). Check that the services are running."
    except httpx.TimeoutException:
        return f"❌ Backend error: request timed out ({lms_api_url}). The service may be overloaded."
    except Exception as e:
        error_type = type(e).__name__
        return f"❌ Backend error: {error_type} - {e!s}"
