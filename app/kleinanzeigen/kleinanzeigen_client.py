import aiohttp
import uuid
import random

from loguru import logger

from .models import KleinanzeigenItem
from typing import Optional

class KleinanzeigenClient:
    """Client for Kleinanzeigen.de API (singleton)."""

    _instance: Optional["KleinanzeigenClient"] = None
    _settings = None

    def __init__(self, settings):
        """Initialize the client."""
        self.base_url = settings.KLEINANZEIGEN_API_URL
        self.headers = {
            "User-Agent": "Kleinanzeigen/100.43.3 (Android 9; google G011A)",
            "X-ECG-USER-AGENT": "ebayk-android-app-100.43.3",
            "X-ECG-USER-VERSION": "100.43.3",
            "X-EBAYK-APP": self.generate_custom_id(),
            "Authorization": f"Basic {settings.KLEINANZEIGEN_AUTH_TOKEN}"
        }
        self.search_url = self.base_url + "/ads.json"
        self.detail_url = self.base_url + "/ads/{ad_id}.json"

    @classmethod
    def initialize(cls, settings) -> None:
        """Initialize the singleton with settings."""
        cls._settings = settings
        if cls._instance is None:
            cls._instance = cls(settings)

    @classmethod
    def get_instance(cls) -> "KleinanzeigenClient":
        """Get the singleton instance."""
        if cls._instance is None:
            if cls._settings is None:
                raise RuntimeError("KleinanzeigenClient not initialized. Call initialize() first.")
            cls._instance = cls(cls._settings)
        return cls._instance

    async def fetch_one_item(self, ad_id: str) -> Optional[KleinanzeigenItem]:
        response = await self._fetch(self.detail_url.format(ad_id=ad_id))

        if response is None:
            return None

        first_key = next(iter(response))
        value_data = response[first_key].get("value", {})

        return KleinanzeigenItem(value_data)
    
    async def _fetch(self, url: str, params: dict = {}) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to fetch {url}, status code: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None

    @staticmethod
    def generate_custom_id(extra_digits: int = 13) -> str:
        base_uuid = str(uuid.uuid4())
        random_digits = ''.join(random.choices('0123456789', k=extra_digits))
        return base_uuid + random_digits
