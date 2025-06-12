import os
import httpx

CRYPTO_PAY_URL = os.getenv('CRYPTO_PAY_URL', 'https://pay.crypt.bot')
CRYPTO_PAY_TOKEN = os.getenv('CRYPTO_PAY_TOKEN', '')

class CryptoPayAPI:
    """Minimal Crypto Pay API wrapper."""

    def __init__(self):
        self.client = httpx.AsyncClient(headers={'Crypto-Pay-API-Token': CRYPTO_PAY_TOKEN})
        self.base_url = CRYPTO_PAY_URL.rstrip('/')

    async def create_invoice(self, amount: str, description: str, asset: str = 'TON') -> str:
        """Create invoice and return payment URL."""
        payload = {
            'asset': asset,
            'amount': amount,
            'description': description,
        }
        resp = await self.client.post(f'{self.base_url}/api/createInvoice', json=payload)
        resp.raise_for_status()
        data = resp.json()
        if not data.get('ok'):
            raise RuntimeError(f"API error: {data}")
        return data['result']['pay_url']

    async def get_invoice(self, invoice_id: int):
        resp = await self.client.get(f'{self.base_url}/api/getInvoices', params={'invoice_ids': invoice_id})
        resp.raise_for_status()
        data = resp.json()
        if not data.get('ok'):
            raise RuntimeError(f"API error: {data}")
        items = data.get('result', {}).get('items', [])
        return items[0] if items else None
