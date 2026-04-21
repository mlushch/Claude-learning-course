from datetime import date

import httpx
from mcp.server.fastmcp import FastMCP

from api_client import TaskApiClient

mcp = FastMCP("task-manager")
client = TaskApiClient()


def _http_error(exc: httpx.HTTPStatusError) -> dict:
    return {"error": exc.response.text or str(exc), "status_code": exc.response.status_code}


# ── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
async def get_all_tasks(status: str | None = None) -> list[dict]:
    """Return all tasks. Optionally filter by status: Open, InProgress, Completed."""
    try:
        return await client.get_tasks(status)
    except httpx.HTTPStatusError as exc:
        return [_http_error(exc)]


@mcp.tool()
async def get_task(task_id: str) -> dict:
    """Fetch a single task by its UUID. Returns an error dict if not found."""
    try:
        return await client.get_task(task_id)
    except httpx.HTTPStatusError as exc:
        return _http_error(exc)


@mcp.tool()
async def add_task(
    title: str,
    description: str | None = None,
    priority: str = "Medium",
    due_date: str | None = None,
) -> dict:
    """Create a new task. Priority: Low | Medium | High. due_date: ISO 8601 (YYYY-MM-DD)."""
    data: dict = {"title": title, "priority": priority}
    if description:
        data["description"] = description
    if due_date:
        data["dueDate"] = due_date
    try:
        return await client.create_task(data)
    except httpx.HTTPStatusError as exc:
        return _http_error(exc)


@mcp.tool()
async def update_task(
    task_id: str,
    title: str | None = None,
    status: str | None = None,
    priority: str | None = None,
    description: str | None = None,
    due_date: str | None = None,
) -> dict:
    """Update fields on an existing task. All fields optional. Status: Open | InProgress | Completed."""
    data: dict = {}
    if title is not None:
        data["title"] = title
    if status is not None:
        data["status"] = status
    if priority is not None:
        data["priority"] = priority
    if description is not None:
        data["description"] = description
    if due_date is not None:
        data["dueDate"] = due_date
    try:
        return await client.update_task(task_id, data)
    except httpx.HTTPStatusError as exc:
        return _http_error(exc)


@mcp.tool()
async def delete_task(task_id: str) -> dict | str:
    """Delete a task by its UUID. Returns a confirmation message or error dict."""
    try:
        await client.delete_task(task_id)
        return f"Task {task_id} deleted successfully."
    except httpx.HTTPStatusError as exc:
        return _http_error(exc)


# ── Resources ────────────────────────────────────────────────────────────────


@mcp.resource("tasks://all")
async def resource_all_tasks() -> list[dict]:
    """Structured read-only access to all tasks."""
    return await client.get_tasks()


@mcp.resource("tasks://completed")
async def resource_completed_tasks() -> list[dict]:
    """All tasks with status Completed."""
    return await client.get_tasks(status="Completed")


@mcp.resource("tasks://today")
async def resource_today_tasks() -> list[dict]:
    """Tasks whose dueDate is today (UTC)."""
    tasks = await client.get_tasks()
    today = date.today().isoformat()
    return [t for t in tasks if isinstance(t.get("dueDate"), str) and t["dueDate"].startswith(today)]


@mcp.resource("tasks://in-progress")
async def resource_in_progress_tasks() -> list[dict]:
    """All tasks with status InProgress."""
    return await client.get_tasks(status="InProgress")


# ── Prompts ──────────────────────────────────────────────────────────────────


@mcp.prompt()
async def daily_plan() -> str:
    """Get the top 3 highest-priority open tasks to create a focused daily plan."""
    tasks = await client.get_tasks(status="Open")
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    sorted_tasks = sorted(tasks, key=lambda t: priority_order.get(t.get("priority", "Low"), 3))
    top3 = sorted_tasks[:3]
    task_list = "\n".join(f"- {t['title']} [{t.get('priority', 'Medium')}]" for t in top3)
    return f"Here are your top 3 priority tasks for today:\n{task_list}\n\nPlease create a focused daily plan."


@mcp.prompt()
async def prioritize_tasks() -> str:
    """Review all open tasks and suggest a prioritized execution order."""
    tasks = await client.get_tasks(status="Open")
    task_list = "\n".join(
        f"- {t['title']} (Priority: {t.get('priority', 'Medium')}, Due: {t.get('dueDate') or 'N/A'})"
        for t in tasks
    )
    return (
        f"Here are all open tasks:\n{task_list}\n\n"
        "Please analyze and suggest the optimal execution order."
    )


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Task Manager MCP server")
    parser.add_argument("--transport", choices=["stdio", "sse", "streamable-http"], default="stdio")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    args = parser.parse_args()

    if args.transport != "stdio":
        mcp.settings.host = args.host
        mcp.settings.port = args.port

    mcp.run(transport=args.transport)
