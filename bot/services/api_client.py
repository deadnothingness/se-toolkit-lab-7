"""LMS API client with Bearer token authentication.

This service handles all HTTP requests to the LMS backend.
It uses httpx for async/sync HTTP client functionality.
"""

import httpx


class LMSClient:
    """Client for the LMS backend API.

    Uses Bearer token authentication for all requests.
    """

    def __init__(self, base_url: str, api_key: str):
        """Initialize the LMS client.

        Args:
            base_url: Base URL of the LMS backend (e.g., http://localhost:42002).
            api_key: API key for Bearer token authentication.
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            timeout=10.0,
        )

    def get_items(self) -> list[dict]:
        """Fetch all items (labs and tasks) from the backend.

        Returns:
            List of items from the backend.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/items/")
        response.raise_for_status()
        return response.json()

    def get_pass_rates(self, lab: str) -> list[dict]:
        """Fetch pass rates for a specific lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            List of pass rate data per task.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/pass-rates", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def health_check(self) -> dict:
        """Check if the backend is healthy by fetching items count.

        Returns:
            Dict with health status and item count.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        items = self.get_items()
        return {"healthy": True, "item_count": len(items)}

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_client(base_url: str, api_key: str) -> LMSClient:
    """Create an LMS client instance.

    Args:
        base_url: Base URL of the LMS backend.
        api_key: API key for authentication.

    Returns:
        Configured LMSClient instance.
    """
    return LMSClient(base_url, api_key)
