import enum

class BaseEnum(enum.Enum):
    @classmethod
    def from_str(cls, value: str):
        if not value:
            return cls.OTHER
        value_upper = value.upper()
        if value_upper in cls.__members__:
            return cls[value_upper]
        return cls.OTHER

class ItemPriceType(BaseEnum):
    """Price type: Specified amount or Deal possible"""
    SPECIFIED_AMOUNT = "SPECIFIED_AMOUNT"
    PLEASE_CONTACT = "PLEASE_CONTACT"
    OTHER = "OTHER"

class ItemAdType(BaseEnum):
    """Ad type: Wanted or Offered"""
    OFFERED = "OFFERED"
    WANTED = "WANTED"
    OTHER = "OTHER"

class ItemPosterType(BaseEnum):
    """Poster type: Commercial or Private"""
    COMMERCIAL = "COMMERCIAL"
    PRIVATE = "PRIVATE"
    OTHER = "OTHER"

class SellerAccountType(BaseEnum):
    """Seller account type: Commercial or Private"""
    COMMERCIAL = "COMMERCIAL"
    PRIVATE = "PRIVATE"
    OTHER = "OTHER"

class ItemAdStatus(BaseEnum):
    """Ad status: Active or Inactive"""
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    OTHER = "OTHER"
