"""Labs list command handler."""

import httpx
from services.api_client import create_client


def handle_labs(lms_api_url: str, lms_api_key: str) -> str:
    """Handle the /labs command.

    Args:
        lms_api_url: LMS backend URL from config.
        lms_api_key: LMS API key from config.

    Returns:
        List of available labs from the backend.
    """
    try:
        with create_client(lms_api_url, lms_api_key) as client:
            items = client.get_items()

            # Filter for labs (items with type "lab")
            labs = []
            for item in items:
                item_type = item.get("type", "").lower()

                if item_type == "lab":
                    labs.append(item)

            if not labs:
                # If no labs found by filtering, show all unique lab titles from items
                lab_titles = set()
                for item in items:
                    # API uses 'title' field, not 'name'
                    title = item.get("title", item.get("name", ""))
                    if "lab" in title.lower():
                        lab_titles.add(title)

                if lab_titles:
                    labs_list = "\n".join(f"• {title}" for title in sorted(lab_titles))
                    return f"📚 Available labs:\n\n{labs_list}"
                else:
                    return "📚 No labs found in the backend."

            # Format lab list - API uses 'title' field
            labs_list = "\n".join(
                f"• {lab.get('title', lab.get('name', 'Unknown'))}"
                for lab in labs
            )
            return f"📚 Available labs:\n\n{labs_list}"

    except httpx.ConnectError as e:
        error_detail = str(e.args[0]) if e.args else "connection error"
        return f"❌ Backend error: {error_detail} ({lms_api_url}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"❌ Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.TimeoutException:
        return f"❌ Backend error: request timed out ({lms_api_url}). The service may be overloaded."
    except Exception as e:
        error_type = type(e).__name__
        return f"❌ Backend error: {error_type} - {e!s}"
