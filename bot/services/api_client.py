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

    def get_learners(self) -> list[dict]:
        """Fetch all enrolled learners and their groups.

        Returns:
            List of learner records.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/learners/")
        response.raise_for_status()
        return response.json()

    def get_scores(self, lab: str) -> list[dict]:
        """Fetch score distribution for a lab (4 buckets).

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            List of score distribution data.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/scores", params={"lab": lab})
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

    def get_timeline(self, lab: str) -> list[dict]:
        """Fetch submission timeline for a lab (submissions per day).

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            List of timeline data points.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/timeline", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_groups(self, lab: str) -> list[dict]:
        """Fetch per-group scores and student counts for a lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            List of group performance data.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/groups", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def get_top_learners(self, lab: str, limit: int = 10) -> list[dict]:
        """Fetch top N learners by score for a lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").
            limit: Maximum number of learners to return (default 10).

        Returns:
            List of top learner records.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get(
            "/analytics/top-learners", params={"lab": lab, "limit": limit}
        )
        response.raise_for_status()
        return response.json()

    def get_completion_rate(self, lab: str) -> dict:
        """Fetch completion rate percentage for a lab.

        Args:
            lab: Lab identifier (e.g., "lab-04").

        Returns:
            Dict with completion rate data.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.get("/analytics/completion-rate", params={"lab": lab})
        response.raise_for_status()
        return response.json()

    def trigger_sync(self) -> dict:
        """Trigger a data sync from autochecker.

        Returns:
            Dict with sync status.

        Raises:
            httpx.HTTPError: If the request fails.
        """
        response = self._client.post("/pipeline/sync")
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
