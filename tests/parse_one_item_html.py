import json
from pathlib import Path
from typing import Dict, List, Optional

from bs4 import BeautifulSoup
from loguru import logger


class ItemDetailParser:
    """Parser for Kleinanzeigen.de item detail page using BeautifulSoup4."""
    
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
    
    def parse_item(self) -> Dict:
        """Parse item details from HTML."""
        try:
            # Get title
            title = self._get_title()
            
            # Get price
            price = self._get_price()
            
            # Get location
            location = self._get_location()
            
            # Get description
            description = self._get_description()
            
            # Get image URLs
            image_urls = self._get_image_urls()
            
            # Get item details
            item_details = self._get_item_details()
            
            # Get seller info
            seller_info = self._get_seller_info()
            
            return {
                'title': title,
                'price': price,
                'location': location,
                'description': description,
                'image_urls': image_urls,
                'item_details': item_details,
                'seller_info': seller_info
            }
        
        except Exception as e:
            logger.error(f"Error parsing item details: {e}")
            return {}
    
    def _get_title(self) -> str:
        """Get item title."""
        title_elem = self.soup.find('h1', id='viewad-title')
        return title_elem.text.strip() if title_elem else ""
    
    def _get_price(self) -> str:
        """Get item price."""
        price_elem = self.soup.find('h2', id='viewad-price')
        return price_elem.text.strip() if price_elem else ""
    
    def _get_location(self) -> str:
        """Get item location."""
        location_elem = self.soup.find('span', id='viewad-locality')
        return location_elem.text.strip() if location_elem else ""
    
    def _get_description(self) -> str:
        """Get item description with line breaks preserved."""
        desc_elem = self.soup.find('p', id='viewad-description-text')
        if desc_elem:
            text = desc_elem.get_text(separator='\n', strip=True)
            # Удаляем лишние пустые строки, но сохраняем формат
            lines = [line.strip() for line in text.splitlines() if line.strip()]
            return '\n'.join(lines)
        return ""

    
    def _get_image_urls(self) -> List[str]:
        """Get all image URLs."""
        image_urls = []
        
        # Find lightbox container
        lightbox = self.soup.find('div', id='viewad-lightbox')
        if lightbox:
            # Find all images in thumbnails
            images = lightbox.find_all('img', attrs={'data-imgsrc': True})
            for img in images:
                if img.get('data-imgsrc'):
                    # Get full resolution image URL with rule
                    image_url = img['data-imgsrc']
                    image_urls.append(image_url)
        
        return list(set(image_urls))  # Remove duplicates
    
    def _get_item_details(self) -> Dict:
        """Get additional item details."""
        details = {}
        
        # Find details list
        details_list = self.soup.find('div', class_='addetailslist')
        if details_list:
            items = details_list.find_all('li', class_='addetailslist--detail')
            for item in items:
                label = item.find('span', class_='addetailslist--detail--value')
                if label:
                    details[item.text.strip().split(label.text)[0].strip()] = label.text.strip()
        
        return details
    
    def _get_seller_info(self) -> Dict:
        """Get seller information."""
        seller_info = {}
        
        # Find seller profile box
        profile_box = self.soup.find('div', id='viewad-profile-box')
        if profile_box:
            # Get seller name
            name_elem = profile_box.find('span', class_='userprofile-vip')
            if name_elem:
                seller_info['name'] = name_elem.text.strip()
            
            # Get seller type
            type_elem = profile_box.find('span', class_='userprofile-vip-details-text')
            if type_elem:
                seller_info['type'] = type_elem.text.strip()
            
            # Get seller active since
            active_elem = profile_box.find_all('span', class_='userprofile-vip-details-text')[-1]
            if active_elem:
                seller_info['active_since'] = active_elem.text.strip()
        
        return seller_info


def main():
    """Main function to run the parser."""
    # Path to your HTML file
    html_file = "html_files/item_result.html"
    
    try:
        # Create parser
        parser = ItemDetailParser(html_file)
        
        # Parse item
        item = parser.parse_item()
        
        # Print results
        print("\nItem Details:")
        print("-" * 50)
        print(f"Title: {item['title']}")
        print(f"Price: {item['price']}")
        print(f"Location: {item['location']}")
        print("\nDescription:")
        print(item['description'])
        print("\nImages:")
        for url in item['image_urls']:
            print(f"- {url}")
        print("\nItem Details:")
        for key, value in item['item_details'].items():
            print(f"{key}: {value}")
        print("\nSeller Info:")
        for key, value in item['seller_info'].items():
            print(f"{key}: {value}")
        
        # Save to JSON file
        output_file = "tests/parsed_item_detail.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(item, f, ensure_ascii=False, indent=2)
        
        print(f"\nResults saved to {output_file}")
    
    except Exception as e:
        logger.error(f"Error running parser: {e}")


if __name__ == "__main__":
    main()
