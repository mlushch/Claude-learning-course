import os
from typing import Any, TypedDict

import httpx
from dotenv import load_dotenv

load_dotenv()


class TaskDict(TypedDict, total=False):
    id: str
    title: str
    description: str | None
    status: str
    priority: str
    dueDate: str | None
    createdAt: str


class TaskApiClient:
    def __init__(self) -> None:
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:5000")
        self.headers = {"X-Api-Key": os.getenv("API_KEY", "")}

    async def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> httpx.Response:
        async with httpx.AsyncClient() as client:
            r = await client.request(
                method,
                f"{self.base_url}{path}",
                headers=self.headers,
                **kwargs,
            )
            r.raise_for_status()
            return r

    async def get_tasks(self, status: str | None = None) -> list[TaskDict]:
        params = {"status": status} if status else {}
        return (await self._request("GET", "/tasks", params=params)).json()

    async def get_task(self, task_id: str) -> TaskDict:
        return (await self._request("GET", f"/tasks/{task_id}")).json()

    async def create_task(self, data: dict[str, Any]) -> TaskDict:
        return (await self._request("POST", "/tasks", json=data)).json()

    async def update_task(self, task_id: str, data: dict[str, Any]) -> TaskDict:
        return (await self._request("PUT", f"/tasks/{task_id}", json=data)).json()

    async def delete_task(self, task_id: str) -> None:
        await self._request("DELETE", f"/tasks/{task_id}")
