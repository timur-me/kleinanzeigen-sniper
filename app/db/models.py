from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, BigInteger
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Enum

from datetime import datetime
from uuid import uuid4

from app.kleinanzeigen.models import KleinanzeigenItem
from app.kleinanzeigen.enums import ItemAdType, ItemPosterType

from .database import Base

class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    username = Column(String, nullable=True)
    first_name = Column(String, nullable=True)
    last_name = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def full_name(self) -> str:
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        elif self.first_name:
            return self.first_name
        elif self.username:
            return self.username
        return str(self.user_id)

class Item(Base):
    __tablename__ = "items"

    id = Column(String, primary_key=True)  # ID от Kleinanzeigen
    raw_data = Column(JSONB, nullable=False)
    first_seen = Column(DateTime, default=datetime.utcnow)
    last_updated = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_kleinanzeigen_item(self) -> KleinanzeigenItem:
        return KleinanzeigenItem(self.raw_data)

class SearchSettings(Base):
    __tablename__ = "search_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    alias = Column(String)
    item_name = Column(String)
    lowest_price = Column(Integer, nullable=True)
    highest_price = Column(Integer, nullable=True)
    location_id = Column(String)
    location_name = Column(String)
    category_id = Column(String, nullable=True)
    category_name = Column(String, nullable=True)
    ad_type: ItemAdType = Column(Enum(ItemAdType, name="item_ad_type", native_enum=False), nullable=True)
    poster_type: ItemPosterType = Column(Enum(ItemPosterType, name="item_poster_type", native_enum=False), nullable=True)
    is_picture_required = Column(Boolean, default=False)
    radius_km = Column(Integer, default=10)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    was_used = Column(Boolean, default=False)

    def mark_as_used(self):
        self.was_used = True
        self.updated_at = datetime.utcnow()

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    item_id = Column(String, ForeignKey('items.id'))
    user_id = Column(BigInteger, ForeignKey('users.user_id'))
    search_id = Column(String, ForeignKey('search_settings.id'))
    is_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    sent_at = Column(DateTime, nullable=True, default=None)

    def mark_as_sent(self):
        self.is_sent = True
        self.sent_at = datetime.utcnow()

class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(String, primary_key=True, default=lambda: str(uuid4()))
    user_id = Column(BigInteger, ForeignKey('users.user_id'), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    default_lowest_price = Column(Integer, default=0, nullable=True)
    default_highest_price = Column(Integer, default=10000, nullable=True)
    default_location_id = Column(String, nullable=True)
    default_location_name = Column(String, nullable=True)
    default_location_radius_km = Column(Integer, default=10)
    default_ad_type: ItemAdType = Column(Enum(ItemAdType, name="default_item_ad_type", native_enum=False), nullable=True)
    default_poster_type: ItemPosterType = Column(Enum(ItemPosterType, name="default_item_poster_type", native_enum=False), nullable=True)
    default_is_picture_required = Column(Boolean, default=False)


