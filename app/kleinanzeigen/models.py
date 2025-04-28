import html

from datetime import datetime
from typing import Optional

from .enums import *
from .utils import parse_date_str, write_date_str
from .types import (
    KleinanzeigenItem as KleinanzeigenItemType,
    KleinanzeigenItemPrice as KleinanzeigenItemPriceType,
    KleinanzeigenItemCategory as KleinanzeigenItemCategoryType,
    KleinanzeigenItemLocation as KleinanzeigenItemLocationType,
    KleinanzeigenPicture as KleinanzeigenPictureType,
    KleinanzeigenSeller as KleinanzeigenSellerType
)

class KleinanzeigenItem(KleinanzeigenItemType):
    def __init__(self, item_data: dict):
        self.__item_data = item_data
        self.__parse_item_data()

    def __parse_item_data(self) -> None:
        self.id = self.__item_data.get("id", None)
        self.title = self.__item_data.get("title", {}).get("value", None)
        self.price = KleinanzeigenItemPrice(self.__item_data.get("price", {}))
        self.ad_type = ItemAdType.from_str(self.__item_data.get("ad-type", {}).get("value", ""))
        self.poster_type = ItemPosterType.from_str(self.__item_data.get("poster-type", {}).get("value", ""))
        self.description = self.__item_data.get("description", {}).get("value", None)
        self.description = html.unescape(self.description).replace("<br />", "\n") if self.description else None
        self.ad_status = ItemAdStatus.from_str(self.__item_data.get("ad-status", {}).get("value", ""))
        self.ad_post_date_str = self.__item_data.get("start-date-time", {}).get("value", None)
        self.ad_post_date = parse_date_str(self.ad_post_date_str) if self.ad_post_date_str else None
        self.ad_post_date_str = write_date_str(self.ad_post_date) if self.ad_post_date else None
        self.category = KleinanzeigenItemCategory(self.__item_data.get("category", {}))
        loc_dict = self.__item_data.get("locations", {}).get("location", [])[0]
        self.location = KleinanzeigenItemLocation(loc_dict) if loc_dict else None
        self.pictures = [KleinanzeigenPicture(picture) for picture in self.__item_data.get("pictures", {}).get("picture", [])]
        self.seller = KleinanzeigenSeller(self.__item_data)
        links = self.__item_data.get("link", [])
        
        self.ad_link = None
        for link in links:
            if link.get("rel") == "self-public-website":
                self.ad_link = link.get("href")
                break

class KleinanzeigenItemPrice(KleinanzeigenItemPriceType):
    def __init__(self, price_data: dict):
        self.__price_data = price_data
        self.__parse_price_data()

    def __parse_price_data(self) -> None:
        self.currency = self.__price_data.get("currency-iso-code", {}).get("value", {}).get("value", "EUR")
        self.amount = self.__price_data.get("amount", {}).get("value", None)
        price_type_value = self.__price_data.get("price-type", {}).get("value", "")
        self.price_type = ItemPriceType.from_str(price_type_value)

class KleinanzeigenSeller(KleinanzeigenSellerType):
    def __init__(self, item_data: dict):
        self.__item_data = item_data
        self.__parse_seller_data()

    def __parse_seller_data(self) -> None:
        self.name = self.__item_data.get("contact-name", {}).get("value", None)
        self.initials = self.__item_data.get("contact-name-initials", {}).get("value", None)
        self.user_id = self.__item_data.get("user-id", {}).get("value", None)
        self.store_id = self.__item_data.get("store-id", {}).get("value", None)
        self.seller_account_type = SellerAccountType.from_str(self.__item_data.get("seller-account-type", {}).get("value", ""))
        self.user_rating = self.__item_data.get("user-rating", {}).get("averageRating", {}).get("value", None)
        self.user_badges = [KleinanzeigenUserBadge(badge) for badge in self.__item_data.get("user-badges", {}).get("badges", [])]
        self.phone = self.__item_data.get("phone", {}).get("value", {})
        self.registration_date_str = self.__item_data.get("user-since-date-time", {}).get("value", None)
        self.registration_date = parse_date_str(self.registration_date_str) if self.registration_date_str else None

class KleinanzeigenItemCategory(KleinanzeigenItemCategoryType):
    def __init__(self, category_data: dict):
        self.__category_data = category_data
        self.__parse_category_data()

    def __parse_category_data(self) -> None:
        self.id_name = self.__category_data.get("id-name", {}).get("value", None)
        self.localized_name = self.__category_data.get("localized-name", {}).get("value", None)

class KleinanzeigenUserBadge:
    def __init__(self, badge_data: dict):
        self.__badge_data = badge_data
        self.__parse_badge_data()

    def __parse_badge_data(self) -> None:
        self.name = self.__badge_data.get("name", None)
        self.level = self.__badge_data.get("level", None)
        self.value = self.__badge_data.get("value", None)

class KleinanzeigenItemLocation(KleinanzeigenItemLocationType):
    def __init__(self, location_data: dict):
        self.__location_data = location_data
        self.__parse_location_data()

    def __parse_location_data(self) -> None:
        self.zip_code = self.__location_data.get("id-name", {}).get("value", None)
        self.zip_code_localized = self.__location_data.get("localized-name", {}).get("value", None)
        self.longitude = self.__location_data.get("longitude", {}).get("value", None)
        self.latitude = self.__location_data.get("latitude", {}).get("value", None)
        self.radius = self.__location_data.get("radius", {}).get("value", None)
        regions = self.__location_data.get("regions", {}).get("region", [])
        if regions:
            self.region = regions[0].get("localized-name", {}).get("value", None)
        else:
            self.region = None

    def __str__(self) -> str:
        return f"{self.region} - {self.zip_code_localized}"

class KleinanzeigenPicture(KleinanzeigenPictureType):
    def __init__(self, picture_data: dict):
        self.thumbnail = None
        self.teaser = None
        self.large = None
        self.extra_large = None
        self.xxl = None
        self.canonical_url = None

        links = picture_data.get("link", [])
        for link in links:
            rel = link.get("rel", "")
            href = link.get("href", "")

            if rel == "thumbnail":
                self.thumbnail = href
            elif rel == "teaser":
                self.teaser = href
            elif rel == "large":
                self.large = href
            elif rel == "extraLarge":
                self.extra_large = href
            elif rel == "XXL":
                self.xxl = href
            elif rel == "canonicalUrl":
                self.canonical_url = href