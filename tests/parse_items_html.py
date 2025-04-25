import json
import re
from pathlib import Path
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from loguru import logger


class ItemParser:
    """Parser for Kleinanzeigen.de items using BeautifulSoup4."""
    
    def __init__(self, html_file: str):
        """Initialize parser with HTML file path."""
        self.html_file = Path(html_file)
        self.soup = self._load_html()
    
    def _load_html(self) -> BeautifulSoup:
        """Load and parse HTML file."""
        if not self.html_file.exists():
            raise FileNotFoundError(f"HTML file not found: {self.html_file}")
        
        with open(self.html_file, 'r', encoding='utf-8') as f:
            return BeautifulSoup(f.read(), 'html.parser')
    
    def parse_items(self) -> List[Dict]:
        """Parse all items from HTML."""
        items = []
        
        # Find all article elements
        articles = self.soup.find_all('article', class_='aditem')
        
        for article in articles:
            try:
                item = self._parse_item(article)
                if item:
                    items.append(item)
            except Exception as e:
                logger.error(f"Error parsing item: {e}")
                continue
        
        return items
    
    def _clean_address(self,raw: str) -> str:
        raw = re.sub(r'\s+', ' ', raw).strip()
        match = re.search(r'(.+?)\s*(\(\d+\s*km\))', raw)
        return f"{match.group(1).strip()} {match.group(2).strip()}" if match else raw
    
    def _parse_item(self, article) -> Optional[Dict]:
        """Parse single item from article element."""
        try:
            # Get item ID
            item_id = article.get('data-adid')
            if not item_id:
                return None
            
            # Get title and URL
            title_elem = article.find('a', class_='ellipsis')
            if not title_elem:
                return None
            
            title = title_elem.text.strip()
            url = title_elem.get('href', '')
            
            # Get price
            price_elem = article.find('p', class_='aditem-main--middle--price-shipping--price')
            price = price_elem.text.strip() if price_elem else None
            
            # Get location
            location_elem = article.find('div', class_='aditem-main--top--left')
            location = location_elem.text.strip() if location_elem else None
            location = self._clean_address(location)
            
            # Get image URL
            image_elem = article.find('img')
            image_url = image_elem.get('src') if image_elem else None
            
            return {
                'id': item_id,
                'title': title,
                'url': url,
                'price': price,
                'location': location,
                'image_url': image_url
            }
        
        except Exception as e:
            logger.error(f"Error parsing item details: {e}")
            return None


def main():
    """Main function to run the parser."""
    # Path to your HTML file
    html_file = "html_files/sample.html"
    
    try:
        # Create parser
        parser = ItemParser(html_file)
        
        # Parse items
        items = parser.parse_items()
        
        # Print results
        print(f"\nFound {len(items)} items:")
        print("-" * 50)
        
        for item in items:
            print(f"ID: {item['id']}")
            print(f"Title: {item['title']}")
            print(f"Price: {item['price']}")
            print(f"Location: {item['location']}")
            print(f"URL: {item['url']}")
            print(f"Image: {item['image_url']}")
            print("-" * 50)
        
        # Save to JSON file
        output_file = "tests/parsed_items.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(items, f, ensure_ascii=False, indent=2)
        
        print(f"\nResults saved to {output_file}")
    
    except Exception as e:
        logger.error(f"Error running parser: {e}")


if __name__ == "__main__":
    main()
