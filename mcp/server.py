from datetime import date

from mcp.server.fastmcp import FastMCP

from api_client import TaskApiClient

mcp = FastMCP("task-manager")
client = TaskApiClient()


# ── Tools ────────────────────────────────────────────────────────────────────


@mcp.tool()
async def get_all_tasks(status: str | None = None) -> list[dict]:
    """Return all tasks. Optionally filter by status: Open, InProgress, Completed."""
    return await client.get_tasks(status)


@mcp.tool()
async def get_task(task_id: str) -> dict:
    """Fetch a single task by its UUID. Returns 404 error if not found."""
    return await client.get_task(task_id)


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
    return await client.create_task(data)


@mcp.tool()
async def update_task(
    task_id: str,
    title: str,
    status: str = "Open",
    priority: str = "Medium",
    description: str | None = None,
    due_date: str | None = None,
) -> dict:
    """Update an existing task. Status: Open | InProgress | Completed."""
    data: dict = {"title": title, "status": status, "priority": priority}
    if description is not None:
        data["description"] = description
    if due_date is not None:
        data["dueDate"] = due_date
    return await client.update_task(task_id, data)


@mcp.tool()
async def delete_task(task_id: str) -> str:
    """Delete a task by its UUID. Returns a confirmation message."""
    await client.delete_task(task_id)
    return f"Task {task_id} deleted successfully."


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
    mcp.run()
