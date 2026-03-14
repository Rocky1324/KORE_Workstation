import httpx
import json

class KOREApiClient:
    def __init__(self, base_url=None, api_key=None):
        self.base_url = base_url
        self.api_key = api_key
        self.client = httpx.AsyncClient(timeout=10.0)

    def set_config(self, base_url, api_key):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    async def check_status(self):
        try:
            headers = {"X-API-KEY": self.api_key}
            response = await self.client.get(f"{self.base_url}/status", headers=headers)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def get_tasks(self):
        try:
            headers = {"X-API-KEY": self.api_key}
            response = await self.client.get(f"{self.base_url}/tasks", headers=headers)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def mark_task_done(self, task_id):
        try:
            headers = {"X-API-KEY": self.api_key}
            response = await self.client.post(f"{self.base_url}/tasks/{task_id}/done", headers=headers)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def send_journal_note(self, title, content):
        try:
            headers = {"X-API-KEY": self.api_key}
            data = {"title": title, "content": content}
            response = await self.client.post(f"{self.base_url}/journal", headers=headers, json=data)
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    async def list_library(self):
        try:
            headers = {"X-API-KEY": self.api_key}
            response = await self.client.get(f"{self.base_url}/library", headers=headers)
            return response.json()
        except Exception as e:
            return {"error": str(e)}
