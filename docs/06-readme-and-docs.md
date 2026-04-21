# Step 6: README & Final Documentation

## Goal

Write the project README and finalize all documentation so the project is self-contained and reproducible.

---

## 6.1 README.md Structure

Create `README.md` in the project root with the following sections:

```markdown
# Task Manager — MCP + Claude Code

A full-stack task management system demonstrating Claude Code integration via a custom MCP server.

## Architecture

[ Claude Code ] → [ MCP Server (Python) ] → [ C# REST API ] → [ In-Memory Storage ]

## Prerequisites

- .NET 8 SDK
- Python 3.11+
- Node.js 18+ (for MCP Inspector)
- Claude Code CLI

## Installation

### 1. Clone the repository

### 2. Start the API

cd api/TaskManager.Api
dotnet run

### 3. Configure environment

cp mcp/.env.example mcp/.env
# Edit mcp/.env with your API key

### 4. Install Python dependencies

cd mcp
python -m venv .venv
.venv\Scripts\activate   # Windows
pip install -r requirements.txt

### 5. Register MCP server with Claude Code

claude mcp add task-manager python mcp/server.py

## Usage

### Via Claude Code

Open the project in Claude Code. The MCP server starts automatically.

Example interactions:
- "Show me all my tasks"
- "Add a high-priority task: Deploy to production"
- "Give me a daily plan"
- "Mark task [ID] as completed"

### Via MCP Inspector

npx @modelcontextprotocol/inspector python mcp/server.py

### Running Tests

# API tests
cd api && dotnet test

# MCP tests
cd mcp && pytest tests/ -v

## Available Skills

- /git-commit — generate a conventional commit message
- /add-test — create a unit test skeleton

## API Reference

All endpoints require the header: X-Api-Key: <your-key>

| Method | Endpoint        | Description        |
|--------|-----------------|--------------------|
| GET    | /tasks          | List all tasks     |
| GET    | /tasks/{id}     | Get task by ID     |
| POST   | /tasks          | Create a task      |
| PUT    | /tasks/{id}     | Update a task      |
| DELETE | /tasks/{id}     | Delete a task      |
| GET    | /health         | Health check       |
```

---

## 6.2 Environment File Template

File: `mcp/.env.example`

```
API_BASE_URL=http://localhost:5000
API_KEY=dev-secret-key-change-me
```

---

## 6.3 .gitignore

Ensure the following are ignored:

```gitignore
# Secrets
.env
*.env.local

# Python
__pycache__/
.venv/
*.pyc
.pytest_cache/

# .NET
bin/
obj/
*.user

# Claude Code
.claude/settings.local.json
```

---

## 6.4 Final Delivery Checklist

Documentation:
- [ ] `README.md` covers prerequisites, installation, usage, API reference
- [ ] `CLAUDE.md` covers project structure, workflow, MCP tools, conventions
- [ ] `mcp/.env.example` exists with all required variables

Code completeness:
- [ ] API builds and runs (`dotnet run`)
- [ ] All 5 API endpoints work with API Key
- [ ] MCP server starts without errors
- [ ] All 5 tools, 4 resources, 2 prompts registered

Claude Code integration:
- [ ] MCP server registered in Claude Code
- [ ] `/git-commit` skill works
- [ ] `/add-test` skill works
- [ ] `code-reviewer` sub-agent invocable
- [ ] `test-writer` sub-agent invocable
- [ ] Pre-edit hook blocks secrets
- [ ] Post-edit hook runs linting + tests

Testing:
- [ ] API xUnit tests pass
- [ ] MCP pytest tests pass
- [ ] MCP Inspector validation complete
- [ ] End-to-end Claude Code flow tested
