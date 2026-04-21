# Step 2: MCP Server (Python)

## Goal

Build a Python MCP server that wraps the C# API and exposes tools, resources, and prompts to Claude Code.

---

## 2.1 Project Setup

```bash
cd mcp/
python -m venv .venv
# Windows
.venv\Scripts\activate
pip install mcp httpx python-dotenv pytest pytest-asyncio
pip freeze > requirements.txt
```

Create `.env`:
```
API_BASE_URL=http://localhost:5000
API_KEY=dev-secret-key-change-me
```

---

## 2.2 API Client

File: `mcp/api_client.py`

Thin wrapper around `httpx.AsyncClient` that:
- Injects `X-Api-Key` header automatically
- Raises `RuntimeError` with a readable message on non-2xx responses
- Exposes async methods: `get_tasks()`, `get_task(id)`, `create_task(data)`, `update_task(id, data)`, `delete_task(id)`

```python
import httpx, os
from dotenv import load_dotenv

load_dotenv()

class TaskApiClient:
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:5000")
        self.headers = {"X-Api-Key": os.getenv("API_KEY", "")}

    async def get_tasks(self, status: str | None = None) -> list[dict]:
        params = {"status": status} if status else {}
        async with httpx.AsyncClient() as client:
            r = await client.get(f"{self.base_url}/tasks",
                                 headers=self.headers, params=params)
            r.raise_for_status()
            return r.json()

    # ... (create_task, get_task, update_task, delete_task follow same pattern)
```

---

## 2.3 MCP Tools

File: `mcp/server.py`

Import and instantiate `mcp.server.FastMCP`. Register the following tools:

| Tool name        | API call                  | Parameters                                         |
|------------------|---------------------------|----------------------------------------------------|
| `get_task`       | `GET /tasks/{id}`         | `task_id: str`                                     |
| `get_all_tasks`  | `GET /tasks`              | `status: str \| None = None`                       |
| `add_task`       | `POST /tasks`             | `title, description, priority, due_date`           |
| `update_task`    | `PUT /tasks/{id}`         | `task_id, title, description, status, priority`    |
| `delete_task`    | `DELETE /tasks/{id}`      | `task_id: str`                                     |

Each tool should have a clear docstring — Claude uses these to understand when and how to call the tool.

```python
from mcp.server.fastmcp import FastMCP
from api_client import TaskApiClient

mcp = FastMCP("task-manager")
client = TaskApiClient()

@mcp.tool()
async def get_all_tasks(status: str | None = None) -> str:
    """Return all tasks. Optionally filter by status: Open, InProgress, Completed."""
    tasks = await client.get_tasks(status)
    return tasks  # MCP serializes to JSON automatically
```

---

## 2.4 MCP Resources

Resources provide structured read-only access to data. Register with `@mcp.resource(uri)`.

| URI                    | Returns                                  |
|------------------------|------------------------------------------|
| `tasks://all`          | All tasks                                |
| `tasks://completed`    | Tasks with `status = Completed`          |
| `tasks://today`        | Tasks whose `dueDate` is today (UTC)     |
| `tasks://in-progress`  | Tasks with `status = InProgress`         |

```python
@mcp.resource("tasks://all")
async def resource_all_tasks() -> list[dict]:
    """Structured access to all tasks."""
    return await client.get_tasks()

@mcp.resource("tasks://today")
async def resource_today_tasks() -> list[dict]:
    """Tasks due today."""
    from datetime import date
    tasks = await client.get_tasks()
    today = date.today().isoformat()
    return [t for t in tasks if t.get("dueDate", "").startswith(today)]
```

---

## 2.5 MCP Prompts

Prompts are reusable AI command templates. Register with `@mcp.prompt()`.

| Prompt name         | Description                                              |
|---------------------|----------------------------------------------------------|
| `daily-plan`        | Gets the top 3 highest-priority tasks for today          |
| `prioritize-tasks`  | Reviews open tasks and suggests a prioritized order      |

```python
@mcp.prompt()
async def daily_plan() -> str:
    """Get the top 3 highest-priority tasks for today to create a daily plan."""
    tasks = await client.get_tasks(status="Open")
    sorted_tasks = sorted(tasks, key=lambda t: {"High": 0, "Medium": 1, "Low": 2}[t["priority"]])
    top3 = sorted_tasks[:3]
    task_list = "\n".join(f"- {t['title']} [{t['priority']}]" for t in top3)
    return f"Here are your top 3 priority tasks for today:\n{task_list}\n\nPlease create a focused daily plan."

@mcp.prompt()
async def prioritize_tasks() -> str:
    """Review all open tasks and suggest a prioritized order."""
    tasks = await client.get_tasks(status="Open")
    task_list = "\n".join(f"- {t['title']} (Priority: {t['priority']}, Due: {t.get('dueDate','N/A')})" for t in tasks)
    return f"Here are all open tasks:\n{task_list}\n\nPlease analyze and suggest the optimal execution order."
```

---

## 2.6 Running the MCP Server

```bash
cd mcp/
python server.py
```

The server listens via **stdio** by default (required for Claude Code integration).

For development/inspection use SSE transport:
```bash
python server.py --transport sse --port 8080
```

---

## 2.7 MCP Inspector Validation

```bash
npx @modelcontextprotocol/inspector python server.py
```

Checklist:
- [ ] All 5 tools appear and can be called
- [ ] All 4 resources appear and return data
- [ ] Both prompts appear and return rendered text
- [ ] Error messages are readable when API is down

---

## 2.8 Tests

File: `mcp/tests/test_api_client.py`

Use `pytest` + `httpx.MockTransport` to mock HTTP calls. Test:
- Successful task list, get, create, update, delete
- `RuntimeError` raised on 401/404/500 responses

```bash
cd mcp/
pytest tests/ -v
```
