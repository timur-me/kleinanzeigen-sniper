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
    def __init__(self, item: KleinanzeigenItemType, search_settings: SearchSettings | None= None):
        self.item = item
        self.search_settings = search_settings
        self.message_text = self._build_message_text()
        self.message_media = self._build_message_media()

    def _build_message_text(self) -> str:
        message_text = ""
        message_text += f"{self.search_settings.alias} was triggered!\n\n" if self.search_settings is not None else ""
        message_text += \
f"""🔍 *Item Details*

[{self.item.title}]({self.item.ad_link})

💰 *Price:* {self.item.price.amount} {self.item.price.currency} {'VB' if self.item.price.price_type == ItemPriceType.PLEASE_CONTACT else ''}
📍 *Location:* {str(self.item.location)}
📅 *Published:* {self.item.ad_post_date_str}

📝 *Description:*\n{self.item.description}\n\n"""

        message_text += \
f"""👤 *Seller:*
 • Name: {self.item.seller.name}
 • Rating: {self.item.seller.user_rating}
 • Member since: {self.item.seller.registration_date.year if self.item.seller.registration_date else 'Unknown'}
""" if self.item.seller.name is not None else ""
        
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
f"""
🔍 *Search name:* `{self.search.alias}`
✏️ *Item name:* `{self.search.item_name}`

💶 *Price range:* `{self.search.lowest_price}` – `{self.search.highest_price}` EUR  
🔍 *Location:* `{self.search.location_name}` (+{self.search.radius_km} km)

🏷️ *Category:* _{self.search.category_name or "Any"}_
🔖 *Ad type:* _{self.search.ad_type.value.capitalize() if self.search.ad_type else "Any"}_
👤 *Poster type:* _{self.search.poster_type.value.capitalize() if self.search.poster_type else "Any"}_
📷 *Photos required:* {"✅ Yes" if self.search.is_picture_required else "❌ No"}

🔄 *Status:* {"✅ Active" if self.search.is_active else "❌ Inactive"}
🗓️ *Created:* {self.search.created_at.strftime('%Y-%m-%d %H:%M')}
"""
        
        return message_text
    

