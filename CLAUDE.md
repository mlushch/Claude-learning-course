# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Task Manager — a system where Claude Code talks to a Python MCP server, which in turn calls a C# REST API. The goal is to learn MCP server development end-to-end. The implementation plan lives in `docs/` (read `docs/00-overview.md` first for full context).

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

`mcp/api_client.py` is the only file that issues HTTP calls — all MCP tools delegate to it. The API key is injected there from the environment; it must never appear in source files.

## Commands

### API (C#)

```bash
cd api/TaskManager.Api && dotnet run          # start API on http://localhost:5000
cd api && dotnet test                          # run all xUnit tests
cd api && dotnet test --filter "MethodName"   # run a single test by name
```

### MCP server (Python)

```bash
cd mcp
python -m venv .venv && .venv/Scripts/activate   # Windows venv setup (one-time)
pip install -r requirements.txt
python server.py                                 # start MCP server (stdio mode)
python server.py --transport sse --port 8080     # dev/inspection mode
pytest tests/ -v                                 # run all MCP tests
pytest tests/test_api_client.py::test_name -v   # run a single test
```

### Linting (Python)

```bash
ruff check mcp/ --fix
black mcp/
```

### MCP Inspector

```bash
npx @modelcontextprotocol/inspector python mcp/server.py
```

## MCP surface

| Kind      | Name / URI             | What it does                                        |
|-----------|------------------------|-----------------------------------------------------|
| Tool      | `get_all_tasks`        | List tasks; optional `status` filter                |
| Tool      | `get_task`             | Fetch one task by ID                                |
| Tool      | `add_task`             | Create a task                                       |
| Tool      | `update_task`          | Mutate fields including status                      |
| Tool      | `delete_task`          | Remove a task                                       |
| Resource  | `tasks://all`          | All tasks (read-only)                               |
| Resource  | `tasks://completed`    | Completed tasks                                     |
| Resource  | `tasks://today`        | Tasks whose dueDate is today (UTC)                  |
| Resource  | `tasks://in-progress`  | In-progress tasks                                   |
| Prompt    | `daily-plan`           | Top 3 open tasks by priority, formatted for planning|
| Prompt    | `prioritize-tasks`     | All open tasks formatted for ordering advice        |

Tool docstrings are the primary interface documentation for Claude — keep them accurate.

## Key conventions

**C#:** PascalCase for types and members; `ConcurrentDictionary` for in-memory storage; DTOs are `record` types with `[MaxLength]` attributes; `CreateTaskDto` uses `[Required]` on Title; `UpdateTaskDto` has all-optional fields (PATCH semantics — only provided fields are written); `ApiKeyMiddleware` runs before all routes except `/health`.

**Python:** PEP 8; `async`/`await` throughout (all `httpx` calls are async); `load_dotenv()` at module load in `api_client.py`; `raise_for_status()` on every response — never swallow HTTP errors.

**Commits:** Conventional Commits (`feat:`, `fix:`, `chore:`, etc.), imperative mood, ≤ 72 chars subject.

## Environment variables

| Variable            | Consumed by      |
|---------------------|------------------|
| `API_KEY`           | `mcp/api_client.py` and `api/appsettings.json` |
| `API_BASE_URL`      | `mcp/api_client.py` (default `http://localhost:5000`) |
| `GITHUB_PAT`        | GitHub MCP server |
| `VENV_PYTHON`       | `.mcp.json` — path to the venv Python binary. Windows: `mcp/.venv/Scripts/python.exe`; macOS/Linux: `mcp/.venv/bin/python` |

Copy `mcp/.env.example` to `mcp/.env` for local development. Never commit `.env`.

## Hooks

Hooks in `hooks/` run automatically via `.claude/settings.json`:

- `pre-edit.sh` — blocks writes that contain hardcoded secrets (regex scan); exits 1 to abort
- `post-edit.sh` — runs `ruff` + `black` on any edited `.py` file, then `pytest` if the file is inside `mcp/`

## Skills and sub-agents

| Name            | Type       | Invocation                 |
|-----------------|------------|----------------------------|
| `git-commit`    | Skill      | `/git-commit`              |
| `add-test`      | Skill      | `/add-test`                |
| `code-reviewer` | Sub-agent  | spawn via Agent tool       |
| `test-writer`   | Sub-agent  | spawn via Agent tool       |

Definitions live in `.claude/skills/` and `.claude/agents/`.

## External MCP servers

All three servers are configured in `.mcp.json` at the project root (Claude Code picks this up automatically). See `docs/07-external-mcp-servers.md` for setup prerequisites (PAT scopes, pyright install, venv path).
