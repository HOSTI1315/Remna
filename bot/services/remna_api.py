import os
import httpx

REMNA_API_URL = os.getenv('REMNA_API_URL', 'https://api.remna.st')
REMNA_API_TOKEN = os.getenv('REMNA_API_TOKEN', '')

class RemnaAPI:
    def __init__(self):
        self.base_url = REMNA_API_URL
        self.token = REMNA_API_TOKEN
        self.client = httpx.AsyncClient(headers={'Authorization': f'Bearer {self.token}'})

    async def create_profile(self, user_id: int, days: int, devices: int = 1) -> str:
        # Simplified request to create a profile and return config string
        payload = {'user_id': user_id, 'days': days, 'devices': devices}
        try:
            r = await self.client.post(f'{self.base_url}/profiles', json=payload)
            r.raise_for_status()
            data = r.json()
            return data.get('config', 'profile-config')
        except Exception:
            return 'profile-config'
