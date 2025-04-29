from typing import List
from aiogram.types import InputMediaPhoto

from app.db.models import SearchSettings
from app.kleinanzeigen.enums import ItemPriceType
from app.kleinanzeigen.types import KleinanzeigenItem as KleinanzeigenItemType

class MessageBuilder:
    """Base class for message builders."""
    def build(self):
        raise NotImplementedError("This method should be implemented by subclasses")
   
    
class SingleItemMessageBuilder(MessageBuilder):
    """Base class for message with single item."""
    def _build_message_text(self):
        raise NotImplementedError("This method should be implemented by subclasses")


class SingleKleinanzeigenItemMessageBuilder(SingleItemMessageBuilder):
    """Builder for a single item message."""
    def __init__(self, item: KleinanzeigenItemType):
        self.item = item
        self.message_text = self._build_message_text()
        self.message_media = self._build_message_media()

    def _build_message_text(self) -> str:
        message_text = \
f"""🔍 *Item Details*

[{self.item.title}]({self.item.ad_link})

💰 *Price:* {self.item.price.amount} {self.item.price.currency} {'VB' if self.item.price.price_type == ItemPriceType.PLEASE_CONTACT else ''}
📍 *Location:* {str(self.item.location)}
📅 *Published:* {self.item.ad_post_date_str}

📝 *Description:*\n{self.item.description}

👤 *Seller:*
 • Name: {self.item.seller.name}
 • Rating: {self.item.seller.user_rating}
 • Member since: {self.item.seller.registration_date.year if self.item.seller.registration_date else 'Unknown'}
"""
        
        return message_text
    
    def _build_message_media(self, message_text: str = "") -> List[InputMediaPhoto]:
        media = []
        
        # Add first image with caption
        for i, image in enumerate(self.item.pictures[:10]):  # Limit to 10 images
            if i == 0:
                # First image with caption
                media.append(InputMediaPhoto(
                    type="photo",
                    media=image.xxl,
                    caption=message_text or self.message_text,
                    parse_mode="Markdown"
                ))
            else:
                # Additional images without caption
                media.append(InputMediaPhoto(type="photo", media=image.xxl))
        
        return media if media else None
    

class SingleSearchMessageBuilder(SingleItemMessageBuilder):
    """Builder for a single search message."""
    def __init__(self, search: SearchSettings):
        self.search = search
        self.message_text = self._build_message_text()

    def _build_message_text(self) -> str:
        message_text = \
f"""📊 *Search Details*

*Item:* {self.search.item_name}
*Location:* {self.search.location_name}
*Radius:* {self.search.radius_km} km
*Status:* {"✅ Active" if self.search.is_active else "❌ Inactive"}
*Created:* {self.search.created_at.strftime('%Y-%m-%d')}
"""
        
        return message_text
    

