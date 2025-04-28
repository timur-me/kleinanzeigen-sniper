from datetime import datetime
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class KleinanzeigenItemPrice:
    currency: str
    amount: Optional[float]
    price_type: str

@dataclass
class KleinanzeigenItemCategory:
    id_name: Optional[str]
    localized_name: Optional[str]

@dataclass
class KleinanzeigenItemLocation:
    zip_code: Optional[str]
    zip_code_localized: Optional[str]
    longitude: Optional[str]
    latitude: Optional[str]
    radius: Optional[str]
    region: Optional[str]

@dataclass
class KleinanzeigenPicture:
    thumbnail: Optional[str]
    teaser: Optional[str]
    large: Optional[str]
    extra_large: Optional[str]
    xxl: Optional[str]
    canonical_url: Optional[str]

@dataclass
class KleinanzeigenSeller:
    name: Optional[str]
    initials: Optional[str]
    user_id: Optional[str]
    store_id: Optional[str]
    seller_account_type: str
    user_rating: Optional[float]
    user_badges: List[dict]
    phone: dict
    registration_date: Optional[datetime]
    registration_date_str: Optional[str]

@dataclass
class KleinanzeigenItem:
    raw_data: dict
    id: Optional[str]
    title: Optional[str]
    price: KleinanzeigenItemPrice
    ad_type: str
    poster_type: str
    description: Optional[str]
    ad_status: str
    ad_post_date: Optional[datetime]
    ad_post_date_str: Optional[str]
    category: KleinanzeigenItemCategory
    location: Optional[KleinanzeigenItemLocation]
    pictures: List[KleinanzeigenPicture]
    ad_link: Optional[str]
    seller: KleinanzeigenSeller 