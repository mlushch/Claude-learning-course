# Project Overview: Task Manager MCP System

## Goal

Build a fully integrated system consisting of:
- A C# REST API with CRUD operations and API Key authentication
- A Python MCP server that exposes the API to Claude Code as tools/resources/prompts
- Claude Code productivity tools: skills, sub-agents, and hooks

## Domain: Task Manager

Chosen domain is **Task Manager** — manage tasks with priority, status, and due date.

## Architecture

```
[ Claude Code ]
      ↓  (MCP protocol via stdio/SSE)
[ MCP Server (Python) ]
      ↓  (HTTP + API Key header)
[ C# Web API (ASP.NET Core) ]
      ↓
[ Storage (in-memory / SQLite) ]
```

## Tech Stack

| Layer        | Technology            |
|--------------|-----------------------|
| Backend API  | C# / ASP.NET Core     |
| MCP Server   | Python 3.11+ / `mcp`  |
| Storage      | In-memory (EF Core)   |
| AI Assistant | Claude Code           |
| Testing      | xUnit (API), pytest (MCP) |

## Directory Structure (Target)

```
claude-learning-course/
├── docs/                   ← implementation plan (this folder)
├── api/                    ← C# ASP.NET Core Web API
│   ├── TaskManager.Api/
│   └── TaskManager.Api.Tests/
├── mcp/                    ← Python MCP server
│   ├── server.py
│   ├── api_client.py
│   ├── requirements.txt
│   └── tests/
├── .claude/
│   ├── skills/             ← custom Claude skills
│   └── agents/             ← sub-agent definitions
├── hooks/                  ← pre/post edit hook scripts
├── CLAUDE.md               ← project guide for Claude Code
└── README.md
```

## Definition of Done Checklist

- [ ] All MCP tools validated via MCP Inspector
- [ ] MCP server connects to Claude Code
- [ ] At least one MCP resource and one MCP prompt defined and working
- [ ] CLAUDE.md documents project structure and workflow
- [ ] At least one skill working (`/git-commit`)
- [ ] At least one sub-agent working (`code-reviewer`)
- [ ] Pre-edit and post-edit hooks in place and triggering
- [ ] README.md explains installation, setup, and usage
