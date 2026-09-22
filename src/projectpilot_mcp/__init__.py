"""A small MCP server for managing personal productivity tasks."""

import logging
import unicodedata

# MCP SDK API reference: https://github.com/modelcontextprotocol/python-sdk
from mcp.server.mcpserver import MCPServer


# This list is intentionally in memory for the first version of the project.
tasks: list[dict[str, str]] = []
MAX_TITLE_LENGTH = 120
ALLOWED_PRIORITIES = frozenset({"low", "medium", "high"})
logger = logging.getLogger(__name__)

server = MCPServer(
    name="ProjectPilot",
    instructions="Use ProjectPilot to manage personal productivity tasks.",
)


def _validate_task_input(title: object, priority: object) -> tuple[str, str]:
    """Validate and normalize task input before it reaches the task store."""
    if not isinstance(title, str):
        raise ValueError("Title must be a string.")

    clean_title = title.strip()
    if not clean_title:
        raise ValueError("Title cannot be empty.")
    if len(clean_title) > MAX_TITLE_LENGTH:
        raise ValueError(f"Title must be {MAX_TITLE_LENGTH} characters or fewer.")
    if any(unicodedata.category(character) == "Cc" for character in clean_title):
        raise ValueError("Title cannot contain control characters.")

    # Reject shell-like syntax even though this server never executes task text.
    dangerous_markers = ("$(", "`", ";", "|", "&&", ">", "<")
    if any(marker in clean_title for marker in dangerous_markers):
        raise ValueError("Title contains unsupported command-like characters.")

    if not isinstance(priority, str):
        raise ValueError("Priority must be a string: low, medium, or high.")
    clean_priority = priority.strip().lower()
    if clean_priority not in ALLOWED_PRIORITIES:
        raise ValueError("Priority must be one of: low, medium, high.")

    return clean_title, clean_priority


def _store_task(task: dict[str, str]) -> None:
    """Store one validated task."""
    tasks.append(task)


@server.tool(description="Create a new task with a title and priority.")
def add_task(title: str, priority: str) -> dict[str, str]:
    """Validate and add a task, returning a safe user-facing result."""
    try:
        clean_title, clean_priority = _validate_task_input(title, priority)
    except ValueError as error:
        return {"status": "error", "message": str(error)}

    try:
        _store_task({"title": clean_title, "priority": clean_priority})
    except Exception:
        # Keep implementation details in local logs, never in the MCP response.
        logger.error("Unexpected task storage failure")
        return {
            "status": "error",
            "message": "Unable to add the task right now. Please try again.",
        }

    return {
        "status": "success",
        "message": "Task added successfully.",
        "title": clean_title,
        "priority": clean_priority,
    }


@server.tool(description="Return all tasks currently stored in memory.")
def list_tasks() -> list[dict[str, str]]:
    """Return all tasks that have been added during this server session."""
    return [task.copy() for task in tasks]


def _build_day_plan() -> str:
    """Build the planning text from the current task list."""
    if not tasks:
        return "There are no tasks yet. Add a few tasks, then plan your day."

    task_lines = "\n".join(
        f"- {task['title']} (priority: {task['priority']})" for task in tasks
    )
    return (
        "Help me organize these tasks for today. Suggest an order, identify "
        "the highest-priority work, and include reasonable breaks.\n\n"
        f"Current tasks:\n{task_lines}"
    )


@server.prompt(description="Help organize the existing tasks into a plan for today.")
def plan_my_day() -> str:
    """Create a planning prompt that includes the user's current tasks."""
    try:
        return _build_day_plan()
    except Exception:
        logger.error("Unexpected daily plan failure")
        return "Unable to create a daily plan right now. Please try again."


def main() -> None:
    """Start the MCP server over the standard input/output transport."""
    server.run()
