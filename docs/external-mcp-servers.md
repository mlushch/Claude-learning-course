# Step 7: External MCP Servers — GitHub & Pylance

## Goal

Connect Claude Code to two external MCP servers:
- **GitHub MCP Server** — interact with GitHub repositories, issues, and pull requests
- **Pylance MCP Server** — Python language intelligence (type checking, hover info, completions)

---

## 7.1 GitHub MCP Server

### What it provides

| Tool / Resource         | Description                                              |
|-------------------------|----------------------------------------------------------|
| `create_issue`          | Open a new GitHub issue                                  |
| `list_issues`           | List issues with filters (state, labels, assignee)       |
| `get_issue`             | Get a single issue by number                             |
| `create_pull_request`   | Open a new PR                                            |
| `list_pull_requests`    | List PRs with filters                                    |
| `get_pull_request`      | Get PR details including diff                            |
| `create_or_update_file` | Commit a file change directly to the repo                |
| `search_code`           | Search across repository code                            |
| `list_commits`          | View commit history                                      |
| `get_file_contents`     | Read any file from a branch                              |

### Prerequisites

1. Generate a GitHub Personal Access Token (PAT):
   - Go to GitHub → Settings → Developer settings → Personal access tokens → Fine-grained tokens
   - Grant: `Contents`, `Issues`, `Pull requests` (read + write)
   - Copy the token

2. Install Node.js 18+ (required by `npx`)

### Installation — Option A: npx (recommended for development)

```bash
# Register with Claude Code globally
claude mcp add github npx -- -y @modelcontextprotocol/server-github

# Set the token (stored in Claude Code's MCP env config)
# Edit ~/.claude/settings.json or use the project-level config below
```

### Installation — Option B: Docker (official GitHub server)

```bash
# Uses the official GitHub-maintained image
claude mcp add github-official -- \
  docker run -i --rm \
  -e GITHUB_PERSONAL_ACCESS_TOKEN \
  ghcr.io/github/github-mcp-server
```

### Project-level configuration

Add to `.claude/mcp_servers.json` in the project root:

```json
{
  "mcpServers": {
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}"
      }
    }
  }
}
```

Store the token in your shell environment (never hardcode it):

```bash
# Add to .bashrc / .zshrc / PowerShell profile
export GITHUB_PAT=ghp_yourTokenHere
```

Or on Windows (PowerShell):
```powershell
[System.Environment]::SetEnvironmentVariable("GITHUB_PAT", "ghp_yourTokenHere", "User")
```

### Verification

After restarting Claude Code, confirm the server loaded:

```
/mcp
```

Expected tools visible: `create_issue`, `list_issues`, `create_pull_request`, etc.

Test in Claude Code chat:
```
List open issues in my GitHub repository
```

### Usage examples with this project

| Ask Claude                                      | Tool called             |
|-------------------------------------------------|-------------------------|
| "Create a GitHub issue for the API auth bug"    | `create_issue`          |
| "Open a PR from feat/mcp-server to main"        | `create_pull_request`   |
| "Show me all open PRs"                          | `list_pull_requests`    |
| "Search the repo for TaskItem"                  | `search_code`           |

---

## 7.2 Pylance MCP Server

### What it provides

Pylance (backed by Pyright) exposes Python language intelligence to Claude Code:

| Capability              | Description                                              |
|-------------------------|----------------------------------------------------------|
| Type checking           | Surface type errors before running code                  |
| Hover information       | Type signatures and docstrings for symbols               |
| Go-to-definition        | Locate where a function or class is defined              |
| Diagnostics             | List all type errors and warnings in a file              |
| Symbol search           | Find all usages of a symbol across the project           |

### Prerequisites

- Python 3.11+
- Node.js 18+
- `pyright` installed globally or in the project venv

```bash
pip install pyright
# or
npm install -g pyright
```

### Installation

```bash
# Install the MCP server package
npm install -g @modelcontextprotocol/server-pyright

# Register with Claude Code
claude mcp add pylance npx -- -y @modelcontextprotocol/server-pyright
```

### Project-level configuration

Add to `.claude/mcp_servers.json`:

```json
{
  "mcpServers": {
    "pylance": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-pyright"],
      "env": {
        "PYRIGHT_PYTHON_PATH": "${workspaceFolder}/mcp/.venv/Scripts/python.exe"
      }
    }
  }
}
```

> **Note:** On Windows set `Scripts/python.exe`; on macOS/Linux use `bin/python`.

### Pyrightconfig

Add `mcp/pyrightconfig.json` to ensure Pyright uses the correct venv and stubs:

```json
{
  "venvPath": ".",
  "venv": ".venv",
  "pythonVersion": "3.11",
  "typeCheckingMode": "basic",
  "reportMissingImports": true,
  "reportMissingModuleSource": false,
  "include": ["."],
  "exclude": ["tests/__pycache__"]
}
```

### Verification

After restarting Claude Code:

```
/mcp
```

Expect tools like `get_diagnostics`, `get_hover`, `get_definition`.

Test in Claude Code chat:
```
Check the Python types in mcp/server.py and report any errors
```

### Usage examples with this project

| Ask Claude                                                    | Capability used         |
|---------------------------------------------------------------|-------------------------|
| "Are there any type errors in api_client.py?"                 | Diagnostics             |
| "What is the return type of `get_tasks`?"                     | Hover / type info       |
| "Find all places where `TaskApiClient` is used"               | Symbol search           |
| "Check if the MCP tool parameters match the API client types" | Type checking           |

---

## 7.3 Combined `.claude/mcp_servers.json`

Complete configuration with all three servers (task-manager + github + pylance):

```json
{
  "mcpServers": {
    "task-manager": {
      "command": "python",
      "args": ["mcp/server.py"],
      "cwd": "${workspaceFolder}",
      "env": {
        "API_BASE_URL": "http://localhost:5000",
        "API_KEY": "${TASK_MANAGER_API_KEY}"
      }
    },
    "github": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_PAT}"
      }
    },
    "pylance": {
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-pyright"],
      "env": {
        "PYRIGHT_PYTHON_PATH": "${workspaceFolder}/mcp/.venv/Scripts/python.exe"
      }
    }
  }
}
```

Store all secrets as environment variables — never commit them to the repo.

---

## 7.4 Environment Variables Reference

| Variable                    | Used by        | Where to set               |
|-----------------------------|----------------|----------------------------|
| `TASK_MANAGER_API_KEY`      | task-manager   | `.env` / shell profile     |
| `GITHUB_PAT`                | github         | Shell profile / OS env     |
| `PYRIGHT_PYTHON_PATH`       | pylance        | Shell profile (optional)   |

---

## 7.5 Verification Checklist

GitHub MCP:
- [ ] PAT created with correct scopes (Contents, Issues, Pull requests)
- [ ] `github` server appears in `/mcp` output
- [ ] `list_issues` returns results for a test repository
- [ ] `create_issue` successfully creates an issue on GitHub

Pylance MCP:
- [ ] `pyright` resolves in the project venv
- [ ] `pyrightconfig.json` points to correct venv path
- [ ] `pylance` server appears in `/mcp` output
- [ ] Diagnostics tool surfaces any existing type errors in `mcp/server.py`

Security:
- [ ] No tokens hardcoded in `mcp_servers.json`
- [ ] `.env` and `*.local` files listed in `.gitignore`
- [ ] Pre-edit hook catches any accidental token leaks
