# Task Manager — Project Runbook

Operational reference for running, testing, and maintaining the Task Manager system.

---

## First-time Setup

### 1 — Environment variables

```bash
cp mcp/.env.example mcp/.env
```

Edit `mcp/.env`:

```
API_BASE_URL=http://localhost:5000
API_KEY=<your-secret-key>
```

The same `API_KEY` value must be set in `api/TaskManager.Api/appsettings.json` (or as an environment variable `API_KEY` before starting the API).

Set shell environment variables used by `.mcp.json`:

```bash
# Windows (PowerShell)
$env:VENV_PYTHON = "mcp/.venv/Scripts/python.exe"
$env:TASK_MANAGER_API_KEY = "<your-secret-key>"
$env:GITHUB_PAT = "<your-github-personal-access-token>"   # optional

# macOS / Linux
export VENV_PYTHON="mcp/.venv/bin/python"
export TASK_MANAGER_API_KEY="<your-secret-key>"
export GITHUB_PAT="<your-github-personal-access-token>"   # optional
```

### 2 — Python virtual environment

```bash
cd mcp
python -m venv .venv

# Windows
.venv/Scripts/activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 3 — .NET restore

The API has no manual restore step — `dotnet run` restores automatically.

---

## Starting Services

### API (C#)

```bash
cd api/TaskManager.Api
dotnet run
# Listening on http://localhost:5000
# Swagger UI: http://localhost:5000/swagger
# Health check: http://localhost:5000/health
```

### MCP server (Python) — standalone

```bash
cd mcp
python server.py                            # stdio mode (used by Claude Code)
python server.py --transport sse --port 8080  # SSE mode for browser inspection
```

The MCP server is normally started automatically by Claude Code via `.mcp.json`.
Run it manually only for debugging or MCP Inspector sessions.

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector python mcp/server.py
```

Provides a browser UI to call MCP tools and inspect responses without Claude Code.

---

## Day-to-day Operations

### Typical development session

1. Start the API: `cd api/TaskManager.Api && dotnet run`
2. Open Claude Code in the project root — the `task-manager` MCP server starts automatically.
3. Use Claude to interact with tasks via natural language or MCP tool calls.

### Using Claude Code skills

| Skill | Invocation | What it does |
|-------|-----------|--------------|
| `/git-commit` | Type in Claude Code | Formats a Conventional Commit message and commits staged changes |
| `/add-test` | Type in Claude Code | Generates a test skeleton for the selected code |

### Using Claude Code sub-agents

Spawn via the Agent tool in a Claude session:

| Sub-agent | Role |
|-----------|------|
| `code-reviewer` | Senior code review across 5 quality dimensions |
| `test-writer` | Generates complete xUnit or pytest test suites |

---

## Testing

### API (xUnit)

```bash
cd api
dotnet test                              # all tests
dotnet test --filter "MethodName"        # single test by name
```

Tests live in `api/TaskManager.Api.Tests/TasksControllerTests.cs`.
They cover: CRUD operations, API key auth, input validation (9 scenarios).

### MCP server (pytest)

```bash
cd mcp
pytest tests/ -v                                    # all tests
pytest tests/test_api_client.py::test_name -v       # single test
```

Tests live in `mcp/tests/` (`test_server.py`, `test_api_client.py`).

### Code quality (Python)

```bash
ruff check mcp/ --fix    # lint and auto-fix
black mcp/               # format
```

Both are run automatically by the post-edit hook on every `.py` file save.

---

## Hooks

Hooks run automatically via `.claude/settings.json` on every file edit inside Claude Code.

| Hook | Trigger | Action |
|------|---------|--------|
| `hooks/pre-edit.sh` | Before any file write | Scans for hardcoded secrets; exits 1 to abort if found |
| `hooks/post-edit.sh` | After any `.py` file write | Runs `ruff --fix` + `black`; runs `pytest` if the file is inside `mcp/` |

The pre-edit hook blocks patterns like `api_key = "..."`, `password = "..."`, `Authorization: Bearer <token>`, and similar.

---

## MCP Surface Reference

### Tools

| Tool | Description |
|------|-------------|
| `get_all_tasks` | List all tasks; optional `status` filter |
| `get_task` | Fetch one task by ID |
| `add_task` | Create a new task |
| `update_task` | Mutate fields including status (PATCH semantics) |
| `delete_task` | Remove a task |

### Resources (read-only)

| URI | Description |
|-----|-------------|
| `tasks://all` | All tasks |
| `tasks://completed` | Completed tasks |
| `tasks://today` | Tasks due today (UTC) |
| `tasks://in-progress` | In-progress tasks |

### Prompts

| Prompt | Description |
|--------|-------------|
| `daily-plan` | Top 3 open tasks by priority, formatted for planning |
| `prioritize-tasks` | All open tasks formatted for ordering advice |

---

## API Reference

Base URL: `http://localhost:5000`

All endpoints (except `/health`) require the header:

```
X-Api-Key: <your-secret-key>
```

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check (no auth required) |
| GET | `/api/tasks` | List tasks (optional `?status=` filter) |
| GET | `/api/tasks/{id}` | Get task by ID |
| POST | `/api/tasks` | Create task |
| PUT | `/api/tasks/{id}` | Update task (PATCH semantics — all fields optional) |
| DELETE | `/api/tasks/{id}` | Delete task |

Swagger UI with full schema documentation: `http://localhost:5000/swagger`

### Task fields

| Field | Type | Notes |
|-------|------|-------|
| `id` | GUID | Auto-generated |
| `title` | string | Required, max 200 chars |
| `description` | string | Optional, max 1000 chars |
| `status` | enum | `Open`, `InProgress`, `Completed` |
| `priority` | enum | `Low`, `Medium`, `High` |
| `dueDate` | DateTime? | ISO 8601, UTC |

---

## Environment Variables Reference

| Variable | Consumed by | Required | Default |
|----------|------------|----------|---------|
| `API_KEY` | `mcp/api_client.py`, `api/appsettings.json` | Yes | — |
| `API_BASE_URL` | `mcp/api_client.py` | No | `http://localhost:5000` |
| `VENV_PYTHON` | `.mcp.json` | Yes (Claude Code) | `mcp/.venv/Scripts/python.exe` |
| `TASK_MANAGER_API_KEY` | `.mcp.json` (passes to MCP server) | Yes (Claude Code) | — |
| `GITHUB_PAT` | GitHub MCP server | No | — |

---

## Troubleshooting

### API returns 401 Unauthorized

- Verify `API_KEY` in `mcp/.env` matches the value in `api/appsettings.json` (or the `API_KEY` environment variable).
- Confirm the `X-Api-Key` header is being sent.

### MCP server fails to start in Claude Code

- Check that `VENV_PYTHON` points to the correct Python binary inside the venv.
- Confirm the venv has dependencies installed: `pip install -r mcp/requirements.txt`.
- Check that `TASK_MANAGER_API_KEY` is set in your shell environment.

### MCP server cannot reach the API

- Ensure the API is running: `curl http://localhost:5000/health`
- Check `API_BASE_URL` in `mcp/.env`.

### Python post-edit hook fails

- Activate the venv before running pytest manually: `source mcp/.venv/bin/activate` (or `.venv/Scripts/activate` on Windows).
- Run `ruff check mcp/ --fix && black mcp/` to clear lint errors before re-saving.

### pre-edit hook blocks a write

- Remove or move any hardcoded secret strings to environment variables.
- Never commit API keys, passwords, tokens, or bearer credentials in source files.

### Tests fail after pulling changes

```bash
# API
cd api && dotnet test

# MCP — reinstall deps in case requirements changed
cd mcp && pip install -r requirements.txt && pytest tests/ -v
```

---

## Commit Conventions

Format: `type(scope): imperative subject ≤ 72 chars`

| Type | When to use |
|------|-------------|
| `feat` | New feature |
| `fix` | Bug fix |
| `chore` | Tooling, deps, config |
| `refactor` | Code change with no behavior change |
| `test` | Adding or fixing tests |
| `docs` | Documentation only |

Use `/git-commit` in Claude Code to auto-format commit messages.
