# Step 3: Claude Code Integration

## Goal

Register the MCP server with Claude Code and create `CLAUDE.md` so Claude understands the project layout and workflows.

---

## 3.1 Register MCP Server with Claude Code

Add the server to Claude Code's MCP configuration. Edit (or create) `.claude/mcp_servers.json` in the project root:

```json
{
  "mcpServers": {
    "task-manager": {
      "command": "python",
      "args": ["mcp/server.py"],
      "cwd": "${workspaceFolder}",
      "env": {
        "API_BASE_URL": "http://localhost:5000",
        "API_KEY": "dev-secret-key-change-me"
      }
    }
  }
}
```

Alternatively, register globally via Claude Code settings:
```bash
claude mcp add task-manager python mcp/server.py
```

Restart Claude Code and verify with:
```
/mcp
```
All 5 tools, 4 resources, and 2 prompts should appear.

---

## 3.2 CLAUDE.md

Create `CLAUDE.md` in the project root. This file is automatically loaded by Claude Code as project context.

```markdown
# Task Manager — Claude Code Guide

## Project Structure

- `api/` — C# ASP.NET Core REST API (port 5000)
- `mcp/` — Python MCP server connecting to the API
- `.claude/skills/` — Custom Claude skills
- `.claude/agents/` — Sub-agent definitions
- `hooks/` — Pre/post edit hook scripts
- `docs/` — Implementation plan

## Development Workflow

### Starting the system

1. Start API: `cd api/TaskManager.Api && dotnet run`
2. The MCP server starts automatically via Claude Code's MCP config

### API Key

All API requests require the header: `X-Api-Key: dev-secret-key-change-me`

### Running tests

- API tests: `cd api && dotnet test`
- MCP tests: `cd mcp && pytest tests/ -v`

## MCP Tools Available

- `get_all_tasks` — list tasks, optionally filter by status
- `get_task` — get a single task by ID
- `add_task` — create a new task
- `update_task` — update task fields
- `delete_task` — remove a task

## MCP Resources

- `tasks://all` — all tasks
- `tasks://completed` — completed tasks
- `tasks://today` — tasks due today
- `tasks://in-progress` — in-progress tasks

## MCP Prompts

- `/daily-plan` — top 3 priority tasks for today
- `/prioritize-tasks` — suggest task execution order

## Skills

- `/git-commit` — generates a conventional commit message
- `/add-test` — creates a test skeleton for selected code

## Conventions

- C# code: follow .NET naming conventions (PascalCase for types, camelCase for locals)
- Python code: PEP 8, `ruff` for linting, `black` for formatting
- Commits: Conventional Commits format (`feat:`, `fix:`, `chore:`)
```

---

## 3.3 Verification Checklist

- [ ] `CLAUDE.md` is in the project root and readable
- [ ] Claude Code loads the MCP server on startup (no errors in `/mcp` output)
- [ ] `get_all_tasks` tool can be invoked from Claude Code chat
- [ ] Resources appear when browsing MCP panel
- [ ] Both prompts trigger correctly from Claude Code
