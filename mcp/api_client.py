import os

import httpx
from dotenv import load_dotenv

load_dotenv()


class TaskApiClient:
    def __init__(self):
        self.base_url = os.getenv("API_BASE_URL", "http://localhost:5000")
        self.headers = {"X-Api-Key": os.getenv("API_KEY", "")}

    async def get_tasks(self, status: str | None = None) -> list[dict]:
        params = {"status": status} if status else {}
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/tasks", headers=self.headers, params=params
            )
            r.raise_for_status()
            return r.json()

    async def get_task(self, task_id: str) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/tasks/{task_id}", headers=self.headers
            )
            r.raise_for_status()
            return r.json()

    async def create_task(self, data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/tasks", headers=self.headers, json=data
            )
            r.raise_for_status()
            return r.json()

    async def update_task(self, task_id: str, data: dict) -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.put(
                f"{self.base_url}/tasks/{task_id}", headers=self.headers, json=data
            )
            r.raise_for_status()
            return r.json()

    async def delete_task(self, task_id: str) -> None:
        async with httpx.AsyncClient() as client:
            r = await client.delete(
                f"{self.base_url}/tasks/{task_id}", headers=self.headers
            )
            r.raise_for_status()
