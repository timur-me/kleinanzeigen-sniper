import random
import re
from typing import List, Optional, Tuple
from urllib.parse import quote, urljoin

import aiohttp
from loguru import logger

from app.config.settings import settings
from app.models.models import Item, SearchSettings


class KleinanzeigenScraper:
    """Service for scraping Kleinanzeigen.de listings."""
    
    def __init__(self):
        """Initialize the scraper with user agents."""
        self.base_url = settings.KLEINANZEIGEN_BASE_URL
        self.user_agents = self._load_user_agents()
    
    def _load_user_agents(self) -> List[str]:
        """Load user agents from file."""
        try:
            with open(settings.USER_AGENTS_FILE, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            # Default user agent if file not found
            logger.warning(f"User agents file {settings.USER_AGENTS_FILE} not found, using default")
            return [
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:89.0) Gecko/20100101 Firefox/89.0"
            ]
    
    def _get_random_user_agent(self) -> str:
        """Get a random user agent from the loaded list."""
        if not self.user_agents:
            return "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        return random.choice(self.user_agents)
    
    def build_search_url(self, search_settings: SearchSettings) -> str:
        """Build search URL based on search settings."""
        # URL encode the search query
        search_query = quote(search_settings.item_name)
        
        # Build the search URL
        url = f"{self.base_url}/s-{search_query}/k0"
        
        # Add location parameters if available
        if search_settings.location:
            url += f"l{quote(search_settings.location)}"
        
        # Add radius parameter if specified
        if search_settings.radius_km > 0:
            url += f"r{search_settings.radius_km}"
        
        return url
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Fetch HTML content from URL."""
        headers = {"User-Agent": self._get_random_user_agent()}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        return await response.text()
                    else:
                        logger.error(f"Failed to fetch {url}, status code: {response.status}")
                        return None
        except Exception as e:
            logger.error(f"Error fetching {url}: {e}")
            return None
    
    async def parse_listings(self, html: str) -> List[Item]:
        """Parse HTML to extract item listings."""
        if not html:
            return []
        
        items = []
        
        # Pattern to match article elements containing listings
        article_pattern = r'<article[^>]*class="[^"]*aditem[^"]*"[^>]*data-adid="([^"]+)"[^>]*>(.+?)</article>'
        
        # Find all article matches
        article_matches = re.finditer(article_pattern, html, re.DOTALL)
        
        for match in article_matches:
            try:
                item_id = match.group(1)
                article_content = match.group(2)
                
                title, url = self._extract_title_and_url(article_content)
                price = self._extract_price(article_content)
                location = self._extract_location(article_content)
                image_url = self._extract_image_url(article_content)
                
                # Skip if we couldn't extract the essential data
                if not (title and url):
                    continue
                
                # Create absolute URL if needed
                if url and not url.startswith('http'):
                    url = urljoin(self.base_url, url)
                
                # Create item
                item = Item(
                    id=item_id,
                    title=title,
                    price=price,
                    location=location,
                    url=url,
                    image_urls=[image_url] if image_url else []
                )
                
                items.append(item)
            
            except Exception as e:
                logger.error(f"Error parsing item: {e}")
                continue
        
        return items
    
    def _extract_title_and_url(self, article_content: str) -> Tuple[Optional[str], Optional[str]]:
        """Extract title and URL from article content."""
        title_pattern = r'<a[^>]*class="[^"]*ellipsis[^"]*"[^>]*href="([^"]+)"[^>]*>([^<]+)</a>'
        title_match = re.search(title_pattern, article_content)
        
        if title_match:
            url = title_match.group(1)
            title = title_match.group(2).strip()
            return title, url
        
        return None, None
    
    def _extract_price(self, article_content: str) -> Optional[str]:
        """Extract price from article content."""
        price_pattern = r'<p[^>]*class="[^"]*aditem-main--middle--price[^"]*"[^>]*>([^<]+)</p>'
        price_match = re.search(price_pattern, article_content)
        
        if price_match:
            return price_match.group(1).strip()
        
        return None
    
    def _extract_location(self, article_content: str) -> Optional[str]:
        """Extract location from article content."""
        location_pattern = r'<div[^>]*class="[^"]*aditem-main--top--left[^"]*"[^>]*>([^<]+)</div>'
        location_match = re.search(location_pattern, article_content)
        
        if location_match:
            return location_match.group(1).strip()
        
        return None
    
    def _extract_image_url(self, article_content: str) -> Optional[str]:
        """Extract image URL from article content."""
        image_pattern = r'<img[^>]*src="([^"]+)"[^>]*>'
        image_match = re.search(image_pattern, article_content)
        
        if image_match:
            return image_match.group(1)
        
        return None
    
    async def get_item_details(self, item: Item) -> Item:
        """Fetch additional details for an item from its detail page."""
        if not item.url:
            return item
        
        html = await self.fetch_page(item.url)
        if not html:
            return item
        
        # Extract description
        description = self._extract_description(html)
        if description:
            item.description = description
        
        # Extract additional images
        image_urls = self._extract_all_image_urls(html)
        if image_urls:
            item.image_urls = image_urls
        
        return item
    
    def _extract_description(self, html: str) -> Optional[str]:
        """Extract description from detail page."""
        description_pattern = r'<div[^>]*id="viewad-description"[^>]*>(.+?)</div>'
        description_match = re.search(description_pattern, html, re.DOTALL)
        
        if description_match:
            # Remove HTML tags
            description = re.sub(r'<[^>]+>', ' ', description_match.group(1))
            # Clean up whitespace
            description = re.sub(r'\s+', ' ', description).strip()
            return description
        
        return None
    
    def _extract_all_image_urls(self, html: str) -> List[str]:
        """Extract all image URLs from detail page."""
        image_urls = []
        
        # Look for image gallery
        gallery_pattern = r'<div[^>]*class="[^"]*galleryimage[^"]*"[^>]*data-imgsrc="([^"]+)"[^>]*>'
        gallery_matches = re.finditer(gallery_pattern, html)
        
        for match in gallery_matches:
            image_urls.append(match.group(1))
        
        return image_urls
    
    async def search(self, search_settings: SearchSettings) -> List[Item]:
        """Perform a search based on settings and return found items."""
        search_url = self.build_search_url(search_settings)
        logger.info(f"Searching with URL: {search_url}")
        
        html = await self.fetch_page(search_url)
        if not html:
            logger.error(f"Failed to fetch search page: {search_url}")
            return []
        
        items = await self.parse_listings(html)
        logger.info(f"Found {len(items)} items in search results")
        
        # Fetch detailed information for each item (in a real app, could be done in parallel)
        detailed_items = []
        for item in items[:5]:  # Limit to first 5 to avoid excessive requests during development
            detailed_item = await self.get_item_details(item)
            detailed_items.append(detailed_item)
        
        return detailed_items


# Singleton instance
scraper = KleinanzeigenScraper() 