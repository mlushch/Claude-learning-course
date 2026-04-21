import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import date
from unittest.mock import AsyncMock, patch

import httpx
import pytest

import server

SAMPLE_TASK = {
    "id": "abc-123",
    "title": "Test task",
    "status": "Open",
    "priority": "Medium",
    "dueDate": None,
    "createdAt": "2024-01-01T00:00:00Z",
}


def _http_error(status_code: int, method: str = "GET", url: str = "http://localhost:5000/tasks") -> httpx.HTTPStatusError:
    request = httpx.Request(method, url)
    response = httpx.Response(status_code)
    return httpx.HTTPStatusError(f"HTTP {status_code}", request=request, response=response)


# ── Tools ─────────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_get_all_tasks_returns_tasks():
    with patch.object(server.client, "get_tasks", new=AsyncMock(return_value=[SAMPLE_TASK])):
        result = await server.get_all_tasks()
    assert result == [SAMPLE_TASK]


@pytest.mark.asyncio
async def test_get_all_tasks_passes_status_filter():
    mock = AsyncMock(return_value=[SAMPLE_TASK])
    with patch.object(server.client, "get_tasks", new=mock):
        await server.get_all_tasks(status="Open")
    mock.assert_called_once_with("Open")


@pytest.mark.asyncio
async def test_get_all_tasks_returns_error_on_failure():
    with patch.object(server.client, "get_tasks", new=AsyncMock(side_effect=_http_error(401))):
        result = await server.get_all_tasks()
    assert isinstance(result, list)
    assert result[0]["status_code"] == 401


@pytest.mark.asyncio
async def test_get_task_returns_task():
    with patch.object(server.client, "get_task", new=AsyncMock(return_value=SAMPLE_TASK)):
        result = await server.get_task("abc-123")
    assert result == SAMPLE_TASK


@pytest.mark.asyncio
async def test_get_task_returns_error_dict_on_404():
    with patch.object(server.client, "get_task", new=AsyncMock(side_effect=_http_error(404))):
        result = await server.get_task("missing")
    assert result["status_code"] == 404
    assert "error" in result


@pytest.mark.asyncio
async def test_add_task_creates_task():
    with patch.object(server.client, "create_task", new=AsyncMock(return_value=SAMPLE_TASK)):
        result = await server.add_task(title="Test task")
    assert result == SAMPLE_TASK


@pytest.mark.asyncio
async def test_add_task_returns_error_on_400():
    with patch.object(server.client, "create_task", new=AsyncMock(side_effect=_http_error(400))):
        result = await server.add_task(title="")
    assert result["status_code"] == 400


@pytest.mark.asyncio
async def test_update_task_sends_only_provided_fields():
    mock = AsyncMock(return_value=SAMPLE_TASK)
    with patch.object(server.client, "update_task", new=mock):
        await server.update_task(task_id="abc-123", title="New title")
    task_id_arg, data_arg = mock.call_args[0]
    assert task_id_arg == "abc-123"
    assert data_arg == {"title": "New title"}
    assert "status" not in data_arg
    assert "priority" not in data_arg


@pytest.mark.asyncio
async def test_update_task_returns_error_on_404():
    with patch.object(server.client, "update_task", new=AsyncMock(side_effect=_http_error(404))):
        result = await server.update_task(task_id="missing", title="X")
    assert result["status_code"] == 404


@pytest.mark.asyncio
async def test_delete_task_returns_confirmation():
    with patch.object(server.client, "delete_task", new=AsyncMock(return_value=None)):
        result = await server.delete_task("abc-123")
    assert "abc-123" in result
    assert "deleted" in result.lower()


@pytest.mark.asyncio
async def test_delete_task_returns_error_on_404():
    with patch.object(server.client, "delete_task", new=AsyncMock(side_effect=_http_error(404))):
        result = await server.delete_task("missing")
    assert result["status_code"] == 404


# ── Resources ─────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_resource_today_tasks_filters_by_date():
    today = date.today().isoformat()
    tasks = [
        {**SAMPLE_TASK, "id": "today", "dueDate": f"{today}T00:00:00Z"},
        {**SAMPLE_TASK, "id": "past", "dueDate": "2020-01-01T00:00:00Z"},
        {**SAMPLE_TASK, "id": "no-date", "dueDate": None},
    ]
    with patch.object(server.client, "get_tasks", new=AsyncMock(return_value=tasks)):
        result = await server.resource_today_tasks()
    assert len(result) == 1
    assert result[0]["id"] == "today"


@pytest.mark.asyncio
async def test_resource_today_tasks_empty_when_none_due():
    tasks = [{**SAMPLE_TASK, "dueDate": "2020-01-01T00:00:00Z"}]
    with patch.object(server.client, "get_tasks", new=AsyncMock(return_value=tasks)):
        result = await server.resource_today_tasks()
    assert result == []


# ── Prompts ───────────────────────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_daily_plan_sorts_by_priority_and_limits_to_3():
    tasks = [
        {**SAMPLE_TASK, "id": "1", "title": "Low task", "priority": "Low"},
        {**SAMPLE_TASK, "id": "2", "title": "High task", "priority": "High"},
        {**SAMPLE_TASK, "id": "3", "title": "Medium task", "priority": "Medium"},
        {**SAMPLE_TASK, "id": "4", "title": "Extra low", "priority": "Low"},
    ]
    with patch.object(server.client, "get_tasks", new=AsyncMock(return_value=tasks)):
        result = await server.daily_plan()
    assert "High task" in result
    assert "Medium task" in result
    assert result.index("High task") < result.index("Low task")
    assert result.count("- ") == 3


@pytest.mark.asyncio
async def test_prioritize_tasks_includes_all_tasks_with_due_date():
    tasks = [
        {**SAMPLE_TASK, "id": "1", "title": "Task A", "priority": "High", "dueDate": "2024-12-31"},
        {**SAMPLE_TASK, "id": "2", "title": "Task B", "priority": "Low", "dueDate": None},
    ]
    with patch.object(server.client, "get_tasks", new=AsyncMock(return_value=tasks)):
        result = await server.prioritize_tasks()
    assert "Task A" in result
    assert "Task B" in result
    assert "2024-12-31" in result
    assert "N/A" in result
