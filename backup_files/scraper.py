import random
from typing import List, Optional

import aiohttp
from loguru import logger

from app.config.settings import settings
from app.models.models import Item, SearchSettings


class KleinanzeigenScraper:
    """Service for fetching listings from Kleinanzeigen.de using the mobile API."""
    
    def __init__(self):
        """Initialize the scraper."""
        self.base_url = "https://api.kleinanzeigen.de/api"
        self.search_url = f"{self.base_url}/ads.json"
        self.detail_url = f"{self.base_url}/ads/{{ad_id}}.json"
        self.headers = {
            "User-Agent": "Kleinanzeigen/100.43.3 (Android 9; google G011A)",
            "X-ECG-USER-AGENT": "ebayk-android-app-100.43.3",
            "X-ECG-USER-VERSION": "100.43.3",
            "X-EBAYK-APP": "b760cd24-4c2a-4cb8-9386-dff025040d6f1745598430588",
            "Authorization": "Basic YW5kcm9pZDpUYVI2MHBFdHRZ"
        }
    
    async def fetch_search_results(self, query: str, page: int = 0, size: int = 20) -> List[dict]:
        """Fetch search results from API."""
        params = {
            "_in": "id,title,description,displayoptions,start-date-time,category.id,category.localized_name,"
                  "ad-address.state,ad-address.zip-code,ad-address.availability-radius-in-km,price,pictures,"
                  "link,features-active,search-distance,negotiation-enabled,attributes,medias,medias.media,"
                  "medias.media.title,medias.media.media-link,buy-now,placeholder-image-present,labels,"
                  "price-reduction,store-id,store-title",
            "q": query,
            "page": str(page),
            "size": str(size),
            "pictureRequired": "false",
            "includeTopAds": "true",
            "buyNowOnly": "false",
            "labelsGenerationEnabled": "true",
            "limitTotalResultCount": "true",
            "sortType": "DATE_DESCENDING"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.search_url, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("{http://www.ebayclassifiedsgroup.com/schema/ad/v1}ads", {}).get("value", {}).get("ad", [])
                    else:
                        logger.error(f"Failed to fetch search results, status code: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Error fetching search results: {e}")
            return []
    
    async def fetch_item_details(self, item_id: str) -> Optional[dict]:
        """Fetch detailed information about a specific item."""
        url = self.detail_url.format(ad_id=item_id)
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"Failed to fetch item details for {item_id}, status code: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching item details for {item_id}: {e}")
            return None
    
    def extract_item_info(self, api_item: dict) -> Item:
        """Extract item information from API response."""
        # Extract basic item info
        item_id = api_item.get("id")
        title = api_item.get("title", {}).get("value", "Unknown")
        
        # Extract price
        price_data = api_item.get("price", {})
        amount = price_data.get("amount", {}).get("value", "")
        currency = price_data.get("currency-iso-code", {}).get("value", {}).get("value", "EUR")
        price_str = f"{amount} {currency}" if amount else None
        
        # Extract location
        location = api_item.get("ad-address", {}).get("state", {}).get("value")
        
        # Extract description
        description = api_item.get("description", {}).get("value", "")
        
        # Extract URL from links
        url = None
        for link in api_item.get("link", []):
            if link.get("rel") == "self-public-website":
                url = link.get("href")
                break
        
        # Extract image URLs (large size)
        image_urls = []
        for picture in api_item.get("pictures", {}).get("picture", []):
            for link in picture.get("link", []):
                if link.get("rel") == "large":
                    image_urls.append(link.get("href"))
                    break
        
        # Create and return Item object
        return Item(
            id=item_id,
            title=title,
            description=description,
            price=price_str,
            location=location,
            url=url or f"https://www.kleinanzeigen.de/s-anzeige/{item_id}",
            image_urls=image_urls
        )
    
    def extract_item_from_details(self, api_item_details: dict) -> Optional[Item]:
        """Extract item from detailed API response."""
        if not api_item_details:
            return None
        
        # Extract ad data from response
        ad_data = api_item_details.get("{http://www.ebayclassifiedsgroup.com/schema/ad/v1}ad", {}).get("value", {})
        
        # If we have valid ad data, proceed
        if ad_data:
            return self.extract_item_info(ad_data)
        
        return None
    
    async def search(self, search_settings: SearchSettings) -> List[Item]:
        """Perform a search based on settings and return found items."""
        logger.info(f"Searching for '{search_settings.item_name}' in {search_settings.location}")
        
        # Get search results
        search_results = await self.fetch_search_results(search_settings.item_name)
        logger.info(f"Found {len(search_results)} items in search results")
        
        items = []
        # Process each search result
        for result in search_results:
            item_id = result.get("id")
            if not item_id:
                continue
            
            # Fetch detailed information
            item_details = await self.fetch_item_details(item_id)
            if item_details:
                item = self.extract_item_from_details(item_details)
                if item:
                    items.append(item)
        
        logger.info(f"Successfully processed {len(items)} items")
        return items


# Singleton instance
scraper = KleinanzeigenScraper() 