import pytest
import respx
import httpx
from api_client import TaskApiClient

BASE_URL = "http://localhost:5000"

SAMPLE_TASK = {"id": "abc-123", "title": "Test task", "status": "Open", "priority": "Medium"}


@pytest.fixture
def client():
    return TaskApiClient()


@respx.mock
@pytest.mark.asyncio
async def test_get_tasks_returns_list(client):
    respx.get(f"{BASE_URL}/tasks").mock(
        return_value=httpx.Response(200, json=[SAMPLE_TASK])
    )
    result = await client.get_tasks()
    assert len(result) == 1
    assert result[0]["title"] == "Test task"


@respx.mock
@pytest.mark.asyncio
async def test_get_tasks_with_status_filter(client):
    respx.get(f"{BASE_URL}/tasks", params={"status": "Open"}).mock(
        return_value=httpx.Response(200, json=[SAMPLE_TASK])
    )
    result = await client.get_tasks(status="Open")
    assert result[0]["status"] == "Open"


@respx.mock
@pytest.mark.asyncio
async def test_get_tasks_raises_on_401(client):
    respx.get(f"{BASE_URL}/tasks").mock(return_value=httpx.Response(401))
    with pytest.raises(httpx.HTTPStatusError):
        await client.get_tasks()


@respx.mock
@pytest.mark.asyncio
async def test_get_task_returns_task(client):
    respx.get(f"{BASE_URL}/tasks/abc-123").mock(
        return_value=httpx.Response(200, json=SAMPLE_TASK)
    )
    result = await client.get_task("abc-123")
    assert result["id"] == "abc-123"


@respx.mock
@pytest.mark.asyncio
async def test_get_task_raises_on_404(client):
    respx.get(f"{BASE_URL}/tasks/missing").mock(
        return_value=httpx.Response(404)
    )
    with pytest.raises(httpx.HTTPStatusError):
        await client.get_task("missing")


@respx.mock
@pytest.mark.asyncio
async def test_create_task_returns_created(client):
    payload = {"title": "New task", "priority": "High"}
    created = {**SAMPLE_TASK, "title": "New task", "priority": "High"}
    respx.post(f"{BASE_URL}/tasks").mock(
        return_value=httpx.Response(201, json=created)
    )
    result = await client.create_task(payload)
    assert result["title"] == "New task"
    assert result["priority"] == "High"


@respx.mock
@pytest.mark.asyncio
async def test_create_task_raises_on_400(client):
    respx.post(f"{BASE_URL}/tasks").mock(return_value=httpx.Response(400))
    with pytest.raises(httpx.HTTPStatusError):
        await client.create_task({})


@respx.mock
@pytest.mark.asyncio
async def test_update_task_returns_updated(client):
    updated = {**SAMPLE_TASK, "status": "InProgress"}
    respx.patch(f"{BASE_URL}/tasks/abc-123").mock(
        return_value=httpx.Response(200, json=updated)
    )
    result = await client.update_task("abc-123", {"title": "Test task", "status": "InProgress"})
    assert result["status"] == "InProgress"


@respx.mock
@pytest.mark.asyncio
async def test_update_task_raises_on_404(client):
    respx.patch(f"{BASE_URL}/tasks/missing").mock(
        return_value=httpx.Response(404)
    )
    with pytest.raises(httpx.HTTPStatusError):
        await client.update_task("missing", {"title": "X"})


@respx.mock
@pytest.mark.asyncio
async def test_delete_task_succeeds(client):
    respx.delete(f"{BASE_URL}/tasks/abc-123").mock(
        return_value=httpx.Response(204)
    )
    await client.delete_task("abc-123")


@respx.mock
@pytest.mark.asyncio
async def test_delete_task_raises_on_404(client):
    respx.delete(f"{BASE_URL}/tasks/missing").mock(
        return_value=httpx.Response(404)
    )
    with pytest.raises(httpx.HTTPStatusError):
        await client.delete_task("missing")


@respx.mock
@pytest.mark.asyncio
async def test_get_tasks_raises_on_500(client):
    respx.get(f"{BASE_URL}/tasks").mock(return_value=httpx.Response(500))
    with pytest.raises(httpx.HTTPStatusError):
        await client.get_tasks()
