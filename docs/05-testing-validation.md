# Step 5: Testing & Validation

## Goal

Ensure every component works correctly in isolation and as an integrated system before final delivery.

---

## 5.1 API Unit Tests (xUnit)

File: `api/TaskManager.Api.Tests/TasksControllerTests.cs`

Test scenarios to cover:

```
GetAll_ReturnsEmptyList_WhenNoTasksExist
GetAll_ReturnsAllTasks_WhenTasksExist
GetAll_FiltersByStatus_WhenStatusProvided
GetById_ReturnsTask_WhenFound
GetById_Returns404_WhenNotFound
Create_Returns201_WithValidInput
Create_Returns400_WhenTitleMissing
Create_Returns400_WhenTitleTooLong
Update_UpdatesTask_WhenFound
Update_Returns404_WhenNotFound
Delete_RemovesTask_WhenFound
Delete_Returns404_WhenNotFound
AnyEndpoint_Returns401_WhenApiKeyMissing
AnyEndpoint_Returns401_WhenApiKeyWrong
```

Run:
```bash
cd api && dotnet test --verbosity normal
```

---

## 5.2 MCP API Client Tests (pytest)

File: `mcp/tests/test_api_client.py`

Use `httpx`'s `MockTransport` or `respx` to mock HTTP calls.

```python
import pytest
import respx
import httpx
from api_client import TaskApiClient

@pytest.fixture
def client():
    return TaskApiClient()

@respx.mock
@pytest.mark.asyncio
async def test_get_tasks_returns_list(client):
    respx.get("http://localhost:5000/tasks").mock(
        return_value=httpx.Response(200, json=[{"id": "abc", "title": "Test"}])
    )
    result = await client.get_tasks()
    assert len(result) == 1
    assert result[0]["title"] == "Test"

@respx.mock
@pytest.mark.asyncio
async def test_get_tasks_raises_on_401(client):
    respx.get("http://localhost:5000/tasks").mock(
        return_value=httpx.Response(401)
    )
    with pytest.raises(Exception):
        await client.get_tasks()
```

Run:
```bash
cd mcp && pytest tests/ -v
```

---

## 5.3 MCP Server Validation via MCP Inspector

MCP Inspector lets you call tools interactively before connecting to Claude Code.

```bash
npx @modelcontextprotocol/inspector python mcp/server.py
```

Validation matrix:

| Component         | Test action                                    | Expected result                          |
|-------------------|------------------------------------------------|------------------------------------------|
| `get_all_tasks`   | Call with no args                              | Returns JSON array                       |
| `get_all_tasks`   | Call with `status="Completed"`                 | Returns only completed tasks             |
| `add_task`        | Call with title only                           | Returns new task with generated ID       |
| `add_task`        | Call with all fields                           | Returns full task object                 |
| `get_task`        | Call with valid ID                             | Returns matching task                    |
| `get_task`        | Call with unknown ID                           | Returns error message                    |
| `update_task`     | Call with changed title                        | Returns updated task                     |
| `delete_task`     | Call with valid ID                             | Returns success confirmation             |
| `tasks://all`     | Read resource                                  | Returns all tasks JSON                   |
| `tasks://today`   | Read resource                                  | Returns tasks due today                  |
| `daily-plan`      | Invoke prompt                                  | Returns formatted prompt string          |
| `prioritize-tasks`| Invoke prompt                                  | Returns formatted prompt string          |

---

## 5.4 End-to-End Integration Test

With both the API and MCP server running, validate through Claude Code:

1. Open Claude Code in the project directory
2. Ask: *"Show me all my tasks"* → should call `get_all_tasks`
3. Ask: *"Add a task: 'Write tests' with high priority"* → should call `add_task`
4. Ask: *"What are my tasks for today?"* → should read `tasks://today`
5. Ask: *"Give me a daily plan"* → should invoke `daily-plan` prompt
6. Ask: *"Mark task [ID] as completed"* → should call `update_task`
7. Ask: *"Delete the task I just completed"* → should call `delete_task`

---

## 5.5 Hook Validation

**Pre-edit hook (secret scanner):**
```bash
# Create a test file with a fake secret
echo 'api_key = "super-secret-value"' > /tmp/test_secret.py
bash hooks/pre-edit.sh /tmp/test_secret.py
# Expected: exit code 1, error message printed
```

**Post-edit hook (linting + tests):**
```bash
# Edit a python file in mcp/ with bad formatting, then trigger hook
bash hooks/post-edit.sh mcp/api_client.py
# Expected: ruff and black run, pytest executes
```

---

## 5.6 Final Checklist

- [ ] All API xUnit tests pass
- [ ] All MCP pytest tests pass
- [ ] All tools validated in MCP Inspector
- [ ] All resources return correct data
- [ ] Both prompts return meaningful text
- [ ] End-to-end flow works through Claude Code
- [ ] Pre-edit hook blocks hardcoded secrets
- [ ] Post-edit hook runs linting and tests
