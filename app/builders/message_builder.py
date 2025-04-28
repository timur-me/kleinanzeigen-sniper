from typing import List
from aiogram.types import InputMediaPhoto

from app.kleinanzeigen.enums import ItemPriceType
from app.kleinanzeigen.types import KleinanzeigenItem as KleinanzeigenItemType

class MessageBuilder:
    def build(self):
        raise NotImplementedError("This method should be implemented by subclasses")


class SingleItemMessageBuilder(MessageBuilder):
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