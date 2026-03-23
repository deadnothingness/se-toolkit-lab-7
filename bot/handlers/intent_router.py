"""Intent router for natural language queries.

This module implements the core intent routing logic:
1. Send user message + tool definitions to LLM
2. Execute tool calls returned by LLM
3. Feed results back to LLM
4. Return final summarized response
"""

import json
import sys
from typing import Any

from services.api_client import LMSClient
from services.llm_client import LLMClient, get_tool_definitions


# System prompt that tells the LLM how to behave
SYSTEM_PROMPT = """You are a helpful assistant for an LMS (Learning Management System). 
You have access to tools that fetch data about labs, students, scores, and analytics.

When a user asks a question:
1. First understand what information they need
2. Call the appropriate tool(s) to get that data
3. Once you have the data, summarize it clearly for the user

Tool usage guidelines:
- Use get_items() to discover what labs exist
- Use get_pass_rates(lab) to compare task difficulty within a lab
- Use get_groups(lab) to compare group performance
- Use get_top_learners(lab, limit) to find top students
- Use get_completion_rate(lab) to see completion percentage
- Use get_timeline(lab) to see submission patterns over time
- Use get_scores(lab) to see score distribution
- Use get_learners() to find student enrollment info
- Use trigger_sync() only if explicitly asked to refresh data

For questions like "which lab has the lowest pass rate":
1. First call get_items() to get all labs
2. Then call get_pass_rates() for each lab
3. Compare the results and identify the lowest
4. Report the answer with specific numbers

Always be specific and include numbers from the data. Don't make up data - only report what the tools return.

If the user's message is a greeting or doesn't relate to LMS data, respond naturally without using tools.
If the message is unclear or seems like gibberish, politely ask for clarification and suggest what you can help with.
"""


def route(
    user_message: str,
    lms_client: LMSClient,
    llm_client: LLMClient,
    debug: bool = True,
) -> str:
    """Route a user message through the LLM with tool calling.

    Args:
        user_message: The user's natural language query.
        lms_client: LMS API client for executing tool calls.
        llm_client: LLM client for getting responses.
        debug: If True, print debug info to stderr.

    Returns:
        The final response to show the user.
    """

    def log(msg: str) -> None:
        """Print debug message to stderr if debug mode is on."""
        if debug:
            print(msg, file=sys.stderr)

    # Initialize conversation with system prompt and user message
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]

    # Get tool definitions
    tools = get_tool_definitions()

    # Tool execution loop - max iterations to prevent infinite loops
    max_iterations = 5
    iteration = 0

    while iteration < max_iterations:
        iteration += 1

        # Call LLM
        response = llm_client.chat(messages, tools=tools)

        # Check if LLM wants to call tools
        tool_calls = response.get("tool_calls")

        if not tool_calls:
            # No tool calls - LLM has a final answer
            content = response.get("content", "")
            log(f"[summary] LLM returned final response ({len(content)} chars)")
            return content

        # Log tool calls
        for tc in tool_calls:
            func = tc.get("function", {})
            log(f"[tool] LLM called: {func.get('name')}({func.get('arguments', '{}')})")

        # Execute each tool call and collect results
        tool_results = []
        for tc in tool_calls:
            func = tc.get("function", {})
            tool_name = func.get("name")
            tool_args_str = func.get("arguments", "{}")

            try:
                tool_args = json.loads(tool_args_str) if tool_args_str else {}
            except json.JSONDecodeError:
                tool_args = {}

            # Execute the tool
            result = execute_tool(tool_name, tool_args, lms_client)
            result_str = json.dumps(result, default=str)
            log(f"[tool] Result: {len(result_str)} chars")

            tool_results.append(
                {
                    "type": "function",
                    "tool_call_id": tc.get("id"),
                    "name": tool_name,
                    "content": result_str,
                }
            )

        log(f"[summary] Feeding {len(tool_results)} tool result(s) back to LLM")

        # Add assistant's message with tool calls to conversation
        messages.append(
            {
                "role": "assistant",
                "content": response.get("content"),
                "tool_calls": tool_calls,
            }
        )

        # Add tool results to conversation
        for tr in tool_results:
            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": tr["tool_call_id"],
                    "content": tr["content"],
                }
            )

    # Max iterations reached - return what we have
    log("[warning] Max iterations reached, returning partial result")
    return "I'm having trouble completing this request. Let me summarize what I found so far: " + str(
        messages[-1].get("content", "")
    )[:500]


def execute_tool(name: str, args: dict[str, Any], client: LMSClient) -> Any:
    """Execute a tool by calling the appropriate LMS client method.

    Args:
        name: Tool/function name.
        args: Arguments to pass to the tool.
        client: LMS client instance.

    Returns:
        The result from the tool execution.

    Raises:
        ValueError: If the tool name is unknown.
    """
    tool_map = {
        "get_items": lambda: client.get_items(),
        "get_learners": lambda: client.get_learners(),
        "get_scores": lambda: client.get_scores(**args),
        "get_pass_rates": lambda: client.get_pass_rates(**args),
        "get_timeline": lambda: client.get_timeline(**args),
        "get_groups": lambda: client.get_groups(**args),
        "get_top_learners": lambda: client.get_top_learners(**args),
        "get_completion_rate": lambda: client.get_completion_rate(**args),
        "trigger_sync": lambda: client.trigger_sync(),
    }

    if name not in tool_map:
        raise ValueError(f"Unknown tool: {name}")

    return tool_map[name]()


def is_greeting_or_gibberish(message: str) -> tuple[bool, str | None]:
    """Check if a message is a greeting or gibberish that doesn't need tool calls.

    This is a lightweight pre-check to handle common cases without LLM overhead.

    Args:
        message: The user's message.

    Returns:
        Tuple of (is_simple, response_or_none).
        If is_simple is True and response is not None, return that response directly.
        If is_simple is True and response is None, still send to LLM (it's gibberish).
        If is_simple is False, send to LLM for full processing.
    """
    msg_lower = message.strip().lower()
    msg_stripped = message.strip()

    # Simple greetings - respond directly without LLM
    greetings = {
        "hello": "Hello! I'm your LMS assistant. I can help you with information about labs, scores, pass rates, and student performance. What would you like to know?",
        "hi": "Hi there! I'm here to help with LMS data. Ask me about labs, scores, or student performance!",
        "hey": "Hey! What can I help you with? I can show you lab info, scores, pass rates, and more.",
        "good morning": "Good morning! Ready to check some LMS data? I can help with labs, scores, and analytics.",
        "good afternoon": "Good afternoon! What would you like to know about the LMS?",
        "good evening": "Good evening! I'm here to help with LMS information. What do you need?",
    }

    for greeting, response in greetings.items():
        if msg_lower == greeting or msg_lower.startswith(greeting + " "):
            return (True, response)

    # Check for gibberish (very short, no spaces, mostly non-alphabetic)
    if len(msg_stripped) < 4 and not any(c.isalpha() for c in msg_stripped):
        return (
            True,
            "I didn't understand that. Try asking about labs, scores, pass rates, or student performance!",
        )

    # Check for obvious gibberish patterns (repeated chars, no vowels, etc.)
    if len(msg_stripped) < 10 and msg_stripped.isalpha():
        # Check for very few unique characters (e.g., "aaa", "bbbb")
        if len(set(msg_lower)) < 3:
            return (
                True,
                "I'm not sure what you're asking. Try something like 'what labs are available?' or 'show me scores for lab 4'.",
            )
        # Check for no vowels (English words typically have vowels)
        vowels = set("aeiou")
        if not any(c in vowels for c in msg_lower):
            return (
                True,
                "I didn't understand that. Try asking a question about labs, scores, or student performance!",
            )

    # Check for random-looking short strings without spaces
    if len(msg_stripped) < 8 and " " not in msg_stripped and msg_stripped.isalpha():
        # Common question patterns that should NOT be treated as gibberish
        question_starts = ["what", "which", "how", "who", "show", "list", "get", "tell"]
        if not any(msg_lower.startswith(q) for q in question_starts):
            # Doesn't look like a real question - likely gibberish
            return (
                True,
                "I'm not sure what you're asking. Try something like 'what labs are available?' or 'show me scores for lab 4'.",
            )

    # Not a simple case - send to LLM
    return (False, None)
