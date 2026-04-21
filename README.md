# Task Manager — MCP + Claude Code

A full-stack task management system demonstrating Claude Code integration via a custom MCP server.

## Architecture

```
[ Claude Code ]
      ↓  MCP via stdio
[ mcp/server.py  (Python / FastMCP) ]
      ↓  HTTP + X-Api-Key header
[ api/TaskManager.Api  (ASP.NET Core, port 5000) ]
      ↓
[ In-memory ConcurrentDictionary ]
```

## Directory Structure

```
claude-learning-course/
├── api/                        ← C# ASP.NET Core Web API
│   ├── TaskManager.Api/        ← Controllers, Models, DTOs, Middleware
│   └── TaskManager.Api.Tests/  ← xUnit integration tests
├── mcp/                        ← Python MCP server
│   ├── server.py               ← FastMCP tools, resources, prompts
│   ├── api_client.py           ← Async httpx wrapper for the REST API
│   ├── tests/                  ← pytest tests with respx mocks
│   └── requirements.txt
├── .claude/
│   ├── skills/                 ← /git-commit and /add-test slash commands
│   ├── agents/                 ← code-reviewer and test-writer sub-agents
│   └── settings.json           ← hooks + permissions
├── hooks/
│   ├── pre-edit.sh             ← Secret scanner (blocks hardcoded secrets)
│   └── post-edit.sh            ← Linting + pytest after Python edits
├── docs/                       ← Implementation plan (steps 0–6)
├── CLAUDE.md                   ← Project guide loaded by Claude Code
└── README.md
```

## Prerequisites

| Tool | Version |
|------|---------|
| .NET SDK | 8+ (tested on 10) |
| Python | 3.11+ |
| Node.js | 18+ (for MCP Inspector) |
| Claude Code CLI | latest |

## Installation & Setup

### 1. Clone the repository

```bash
git clone https://github.com/mlushch/Claude-learning-course.git
cd Claude-learning-course
```

### 2. Start the C# API

```bash
cd api/TaskManager.Api
dotnet run
# API available at http://localhost:5000
# Swagger UI at http://localhost:5000/swagger
```

### 3. Configure MCP environment

```bash
cp mcp/.env.example mcp/.env
# Edit mcp/.env if you want a different API key (default: dev-secret-key-change-me)
```

### 4. Install Python dependencies

```bash
cd mcp
python -m venv .venv

# Windows
.venv\Scripts\activate

# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### 5. Register MCP server with Claude Code

The server is already pre-configured in `.mcp.json` at the project root — Claude Code
picks it up automatically. To register it manually instead:

```bash
claude mcp add task-manager python mcp/server.py
```

Verify the server loaded with `/mcp` inside Claude Code.

---

## Running Tests

### API tests (xUnit)

```bash
cd api
dotnet test --verbosity normal
```

Expected: **15 tests passing**

### MCP server tests (pytest)

```bash
cd mcp
pytest tests/ -v
```

Expected: **12 tests passing**

---

## API Reference

All endpoints require the header `X-Api-Key: dev-secret-key-change-me` (except `/health`).

| Method | Endpoint | Description | Body / Query |
|--------|----------|-------------|--------------|
| GET | `/health` | Health check (no auth required) | — |
| GET | `/tasks` | List all tasks | `?status=Open\|InProgress\|Completed` |
| GET | `/tasks/{id}` | Get task by ID | — |
| POST | `/tasks` | Create a task | `CreateTaskDto` |
| PUT | `/tasks/{id}` | Update a task | `UpdateTaskDto` |
| DELETE | `/tasks/{id}` | Delete a task | — |

### CreateTaskDto

```json
{
  "title": "Deploy to production",
  "description": "Optional description",
  "priority": "High",
  "dueDate": "2026-04-30T00:00:00Z"
}
```

### UpdateTaskDto

```json
{
  "title": "Deploy to production",
  "description": "Optional description",
  "status": "InProgress",
  "priority": "High",
  "dueDate": "2026-04-30T00:00:00Z"
}
```

### curl examples

```bash
API_KEY="dev-secret-key-change-me"
BASE="http://localhost:5000"

# Health check (no key needed)
curl $BASE/health

# List all tasks
curl -H "X-Api-Key: $API_KEY" $BASE/tasks

# Create a task
curl -X POST $BASE/tasks \
  -H "X-Api-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title":"Write tests","priority":"High"}'

# Filter by status
curl -H "X-Api-Key: $API_KEY" "$BASE/tasks?status=Open"

# Update a task (replace <id> with actual UUID)
curl -X PUT $BASE/tasks/<id> \
  -H "X-Api-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"title":"Write tests","status":"Completed","priority":"High"}'

# Delete a task
curl -X DELETE $BASE/tasks/<id> -H "X-Api-Key: $API_KEY"
```

---

## MCP Surface

### Tools

| Tool | Description |
|------|-------------|
| `get_all_tasks` | List tasks; optional `status` filter |
| `get_task` | Fetch one task by UUID |
| `add_task` | Create a task |
| `update_task` | Mutate fields including status |
| `delete_task` | Remove a task |

### Resources

| URI | Returns |
|-----|---------|
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

## Usage via Claude Code

With the API running and MCP server registered, open the project in Claude Code and try:

```
"Show me all my tasks"
"Add a high-priority task: Deploy to production"
"What tasks are due today?"
"Give me a daily plan"
"Mark task <ID> as completed"
"Delete the task I just completed"
```

### Via MCP Inspector

```bash
npx @modelcontextprotocol/inspector python mcp/server.py
```

---

## Available Skills

| Skill | Invocation | Description |
|-------|-----------|-------------|
| git-commit | `/git-commit` | Generates a Conventional Commits message from staged changes |
| add-test | `/add-test` | Creates an xUnit / pytest test skeleton for selected code |

---

## Hooks

Hooks run automatically via `.claude/settings.json`:

| Hook | Trigger | Action |
|------|---------|--------|
| `pre-edit.sh` | Before any file edit | Scans for hardcoded secrets; exits 1 to block |
| `post-edit.sh` | After any `.py` file edit | Runs `ruff --fix` + `black`; runs `pytest` for `mcp/` files |

### Manual hook test

```bash
# Should exit 1 and print an error
echo 'api_key = "super-secret-value"' > /tmp/test_secret.py
bash hooks/pre-edit.sh /tmp/test_secret.py

# Should run ruff + black + pytest
bash hooks/post-edit.sh mcp/api_client.py
```

---

## Sub-Agents

| Agent | Description |
|-------|-------------|
| `code-reviewer` | Structured review: correctness, security, quality, conventions |
| `test-writer` | Writes complete runnable tests (no TODO stubs) |

Invoke via the Agent tool in Claude Code conversations.
