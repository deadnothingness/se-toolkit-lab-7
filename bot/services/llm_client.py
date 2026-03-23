"""LLM client for tool-based intent routing.

This service handles communication with the LLM API using the OpenAI-compatible
interface. It supports tool calling for intent-based routing.
"""

import json
import httpx


class LLMClient:
    """Client for LLM API with tool calling support.

    Uses OpenAI-compatible API format for tool definitions and responses.
    """

    def __init__(self, base_url: str, api_key: str, model: str):
        """Initialize the LLM client.

        Args:
            base_url: Base URL of the LLM API (e.g., http://localhost:42005/v1).
            api_key: API key for authentication.
            model: Model name to use (e.g., "coder-model").
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self._client = httpx.Client(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=30.0,
        )

    def chat(
        self,
        messages: list[dict],
        tools: list[dict] | None = None,
        tool_choice: str | dict = "auto",
    ) -> dict:
        """Send a chat request to the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content' keys.
            tools: Optional list of tool definitions (function schemas).
            tool_choice: How to use tools - "auto", "none", or specific tool.

        Returns:
            Dict with the LLM response containing:
            - 'content': Text response (if no tool calls)
            - 'tool_calls': List of tool calls (if LLM decided to use tools)
            - 'finish_reason': Why the response ended

        Raises:
            httpx.HTTPError: If the request fails.
        """
        payload = {
            "model": self.model,
            "messages": messages,
        }

        if tools:
            payload["tools"] = tools
            payload["tool_choice"] = tool_choice

        response = self._client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()

        return data["choices"][0]["message"]

    def close(self) -> None:
        """Close the HTTP client."""
        self._client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


def create_llm_client(base_url: str, api_key: str, model: str) -> LLMClient:
    """Create an LLM client instance.

    Args:
        base_url: Base URL of the LLM API.
        api_key: API key for authentication.
        model: Model name to use.

    Returns:
        Configured LLMClient instance.
    """
    return LLMClient(base_url, api_key, model)


def get_tool_definitions() -> list[dict]:
    """Get tool definitions for all 9 backend endpoints.

    These schemas tell the LLM what tools are available and how to call them.

    Returns:
        List of tool definition dicts in OpenAI function-calling format.
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "get_items",
                "description": "Get the list of all labs and tasks available in the LMS. Use this to discover what labs exist.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_learners",
                "description": "Get the list of all enrolled learners and their group assignments. Use this to find student enrollment info.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_scores",
                "description": "Get score distribution (4 buckets) for a specific lab. Use this to see how scores are distributed.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_pass_rates",
                "description": "Get per-task average pass rates and attempt counts for a lab. Use this to compare difficulty across tasks within a lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_timeline",
                "description": "Get submission timeline showing submissions per day for a lab. Use this to see when students were most active.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_groups",
                "description": "Get per-group average scores and student counts for a lab. Use this to compare group performance or find the best/worst group.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_top_learners",
                "description": "Get top N learners by score for a lab. Use this to find the highest performing students.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Maximum number of learners to return (default 10)",
                        },
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "get_completion_rate",
                "description": "Get the completion rate percentage for a lab. Use this to see what fraction of students completed the lab.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "lab": {
                            "type": "string",
                            "description": "Lab identifier, e.g., 'lab-01', 'lab-04'",
                        }
                    },
                    "required": ["lab"],
                },
            },
        },
        {
            "type": "function",
            "function": {
                "name": "trigger_sync",
                "description": "Trigger a data sync from autochecker to refresh the analytics data. Use this when data seems stale.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            },
        },
    ]
