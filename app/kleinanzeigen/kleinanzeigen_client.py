import aiohttp
import uuid
import random

from loguru import logger

from app.db.models import SearchSettings
from app.config.settings import settings

from .models import KleinanzeigenItem, KleinanzeigenItemLocation
from typing import List, Optional

class KleinanzeigenClient:
    """Client for Kleinanzeigen.de API (singleton)."""

    _instance: Optional["KleinanzeigenClient"] = None
    _settings = None

    def __init__(self):
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
        self.location_url = self.base_url + "/locations.json"

    async def fetch_one_item(self, ad_id: str) -> Optional[KleinanzeigenItem]:
        response = await self._fetch(self.detail_url.format(ad_id=ad_id))

        if response is None:
            return None

        first_key = next(iter(response))
        value_data = response[first_key].get("value", {})

        return KleinanzeigenItem(value_data)
    
    async def fetch_items(self, search_settings: SearchSettings) -> Optional[List[KleinanzeigenItem]]:
        params = self.get_params(
            search_settings,
            size=settings.KLEINANZEIGEN_MAX_ITEMS_PER_PAGE,
        )

        response = await self._fetch(self.search_url, params)

        if response is None:
            return None
        
        response = response.get("{http://www.ebayclassifiedsgroup.com/schema/ad/v1}ads", {}).get("value", {}).get("ad", [])
        if not response:
            return None
        
        items = [KleinanzeigenItem(item) for item in response]
        return items
    
    async def fetch_locations(self, query: str) -> Optional[List[KleinanzeigenItemLocation]]:
        params = {
            "depth": 1,
            "q": query
        }

        response = await self._fetch(self.location_url, params)

        if response is None:
            return None
        
        response = response.get("{http://www.ebayclassifiedsgroup.com/schema/location/v1}locations", {}).get("value", {}).get("location", [])
        if not response:
            return None
        
        locations = [KleinanzeigenItemLocation(location) for location in response][:10]
        return locations

    async def _fetch(self, url: str, params: dict = {}) -> dict:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to fetch {url}, status code: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
        
    def get_params(self, search_settings: SearchSettings, size: int = 5) -> dict:
        params = {
            # "_in": "id,title,description,displayoptions,start-date-time,category.id,category.localized_name,ad-address.state,ad-address.zip-code,ad-address.availability-radius-in-km,price,pictures,link,features-active,search-distance,negotiation-enabled,attributes,medias,medias.media,medias.media.title,medias.media.media-link,buy-now,placeholder-image-present,labels,price-reduction,store-id,store-title,contact-name,contact-name-initials",
            "q": search_settings.item_name,
            "page": "0",
            "sortType": "DATE_DESCENDING",
            "size": str(size),
            "pictureRequired": str(search_settings.is_picture_required).lower(),
            "minPrice": str(search_settings.lowest_price),
            "maxPrice": str(search_settings.highest_price),
            "includeTopAds": "false",
            "buyNowOnly": "false",
            "labelsGenerationEnabled": "true",
            "limitTotalResultCount": "true"
        }

        if search_settings.ad_type is not None:
            params["adType"] = search_settings.ad_type.name

        if search_settings.poster_type is not None:
            params["posterType"] = search_settings.poster_type.name

        if search_settings.category_id is not None:
            params["categoryId"] = search_settings.category_id

        if search_settings.location_id is not None:
            params["locationId"] = search_settings.location_id

            if search_settings.radius_km is not None:
                params["distance"] = search_settings.radius_km

        return params

    @staticmethod
    def generate_custom_id(extra_digits: int = 13) -> str:
        base_uuid = str(uuid.uuid4())
        random_digits = ''.join(random.choices('0123456789', k=extra_digits))
        return base_uuid + random_digits

    @classmethod
    def get_instance(cls) -> "KleinanzeigenClient":
        """Get the singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
