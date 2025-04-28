import aiohttp
from loguru import logger
from typing import Optional, Dict, Any
from datetime import datetime
import pytz
import html

class KleinanzeigenParser:
    """Parser for Kleinanzeigen.de API."""
    
    def __init__(self):
        """Initialize the parser."""
        self.base_url = "https://api.kleinanzeigen.de/api"
        self.headers = {
            "User-Agent": "Kleinanzeigen/100.43.3 (Android 9; google G011A)",
            "X-ECG-USER-AGENT": "ebayk-android-app-100.43.3",
            "X-ECG-USER-VERSION": "100.43.3",
            "X-EBAYK-APP": "b760cd24-4c2a-4cb8-9386-dff025040d6f1745598430588",
            "Authorization": "Basic YW5kcm9pZDpUYVI2MHBFdHRZ"
        }
        self.berlin_tz = pytz.timezone('Europe/Berlin')
    
    async def fetch_item_details(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed information about a specific item."""
        url = f"{self.base_url}/ads/{item_id}.json"
        
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
    
    def _format_date(self, date_str: str, year_only: bool = False) -> str:
        """Format date string to Berlin timezone"""
        if not date_str:
            return ""
        
        try:
            # Parse the date string
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f%z")
            # Convert to Berlin timezone
            dt_berlin = dt.astimezone(self.berlin_tz)
            if year_only:
                # Return only year for member since
                return dt_berlin.strftime("%Y")
            else:
                return dt_berlin.strftime("%Y-%m-%d %H:%M:%S")
        except Exception as e:
            logger.error(f"Error formatting date {date_str}: {e}")
            return date_str
    
    def _get_location_from_regions(self, ad_data: Dict[str, Any]) -> str:
        """Extract location from regions data."""
        location = ""
        try:
            locations = ad_data.get("locations", {}).get("location", [])
            loc = locations[0]
            localized_location = loc.get("localized-name", {}).get("value")
            location = localized_location
            regions = loc.get("regions", {}).get("region", [])
            if regions:
                for region in regions:
                    region_name = region.get("localized-name", {}).get("value")
                    if region_name:
                        location = f"{region_name} - {localized_location}"
                        return location

        except Exception as e:
            logger.error(f"Error extracting location from regions: {e}")
            location = ad_data.get("ad-address", {}).get("state", {}).get("value", "")
        finally:
            return location
    
    def extract_item_info(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract all relevant information from API response."""
        if not data:
            return {}
        
        ad_data = data.get("{http://www.ebayclassifiedsgroup.com/schema/ad/v1}ad", {}).get("value", {})
        if not ad_data:
            return {}
        
        # Extract basic info
        title = ad_data.get("title", {}).get("value", "Unknown")
        
        # Price information
        price_data = ad_data.get("price", {})
        amount = price_data.get("amount", {}).get("value", "")
        currency = price_data.get("currency-iso-code", {}).get("value", {}).get("value", "EUR")
        price_type = price_data.get("price-type", {}).get("value", "")
        price_str = f"{amount} {currency}" if amount else "Price not specified"
        if price_type == "PLEASE_CONTACT":
            price_str += " VB"
        
        # Location information
        location = self._get_location_from_regions(ad_data)
        
        # Dates
        start_date = ad_data.get("start-date-time", {}).get("value", "")
        start_date = self._format_date(start_date, year_only=False)
        last_edit = ad_data.get("last-user-edit-date", {}).get("value", "")
        last_edit = self._format_date(last_edit, year_only=False)

        
        # Seller information
        seller_name = ad_data.get("contact-name", {}).get("value", "")
        seller_rating = ad_data.get("user-rating", {}).get("averageRating", {}).get("value", "")
        seller_since = self._format_date(ad_data.get("user-since-date-time", {}).get("value", ""), year_only=True)
        
        # Description
        description = html.unescape(ad_data.get("description", {}).get("value", "")).replace("<br />", "\n")
        
        # Get public website link
        public_link = None
        for link in ad_data.get("link", []):
            if link.get("rel") == "self-public-website":
                public_link = link.get("href")
                break
        
        # Get image URLs (XXL size)
        image_urls = []
        for picture in ad_data.get("pictures", {}).get("picture", []):
            for link in picture.get("link", []):
                if link.get("rel") == "XXL":
                    image_urls.append(link.get("href"))
                    break
        
        return {
            "title": title,
            "price": price_str,
            "location": location,
            "start_date": start_date,
            "last_edit": last_edit,
            "seller": {
                "name": seller_name,
                "rating": seller_rating,
                "since": seller_since
            },
            "description": description,
            "public_link": public_link,
            "image_urls": image_urls
        }


# Singleton instance
parser = KleinanzeigenParser() 