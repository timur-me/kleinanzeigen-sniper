from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

from app.kleinanzeigen.models import KleinanzeigenItemLocation

from app.db.database import async_session
from app.db.repositories import SearchSettingsRepository


# Main menu keyboard
def get_main_menu() -> ReplyKeyboardMarkup:
    """Create main menu keyboard."""
    keyboard = [
        [
            KeyboardButton(text="🔍 My Searches"),
            KeyboardButton(text="➕ Add Search")
        ],
        [
            KeyboardButton(text="❓ Help"),
            KeyboardButton(text="⚙️ Settings")
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True)


# Search settings keyboard
def get_search_settings_keyboard(search_id: str) -> InlineKeyboardMarkup:
    """Create keyboard for managing a search setting."""
    keyboard = [
        [
            InlineKeyboardButton(text="✏️ Edit", callback_data=f"edit_search:{search_id}"),
            InlineKeyboardButton(text="❌ Delete", callback_data=f"delete_search:{search_id}")
        ],
        [
            InlineKeyboardButton(text="🔄 Toggle Status", callback_data=f"toggle_search:{search_id}")
        ],
        [
            InlineKeyboardButton(text="⬅️ Back", callback_data="back_to_searches")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Confirmation keyboard
def get_confirm_keyboard(action: str, entity_id: str) -> InlineKeyboardMarkup:
    """Create confirmation keyboard."""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Yes", callback_data=f"confirm_{action}:{entity_id}"),
            InlineKeyboardButton(text="❌ No", callback_data=f"cancel_{action}:{entity_id}")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

# Locations keyboard
def get_locations_keyboard(locations: list[KleinanzeigenItemLocation]) -> InlineKeyboardMarkup:
    """Create keyboard for locations."""
    keyboard = []
    for location in locations:
        keyboard.append([InlineKeyboardButton(text=location.zip_code_localized, callback_data=f"select_location:{location.id}:{location.zip_code_localized}")])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Search list pagination keyboard
async def get_search_list_keyboard(search_ids: list, page: int = 0, page_size: int = 5) -> InlineKeyboardMarkup:
    """Create paginated keyboard for search list."""
    keyboard = []
    
    # Calculate pagination
    total_pages = (len(search_ids) + page_size - 1) // page_size
    start_idx = page * page_size
    end_idx = min(start_idx + page_size, len(search_ids))

    # Add search buttons for current page
    for i in range(start_idx, end_idx):
        search_id = search_ids[i]
        async with async_session() as session:
            repo = SearchSettingsRepository(session)
            search_settings = await repo.get_by_id(search_id)

        status_emoji = "✅" if search_settings.is_active else "❌"
        search_name = search_settings.item_name
        keyboard.append([
            InlineKeyboardButton(text=f"{status_emoji} {search_name}", callback_data=f"view_search:{search_id}")
        ])
    
    # Add pagination controls
    pagination_buttons = []
    
    if page > 0:
        pagination_buttons.append(InlineKeyboardButton(text="⬅️ Previous", callback_data=f"search_page:{page-1}"))
    
    if page < total_pages - 1:
        pagination_buttons.append(InlineKeyboardButton(text="Next ➡️", callback_data=f"search_page:{page+1}"))
    
    if pagination_buttons:
        keyboard.append(pagination_buttons)
    
    # Add button to add new search
    keyboard.append([
        InlineKeyboardButton(text="➕ Add New Search", callback_data="add_search")
    ])

    # Cancel button
    keyboard.append([
        get_cancel_button()
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


# Cancel button
def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Create a simple cancel keyboard."""
    keyboard = [
        [get_cancel_button()]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard) 

def get_item_link_keyboard(item_url: str) -> InlineKeyboardMarkup:
    """Create a keyboard with a button to open the item link."""
    open_link_button = InlineKeyboardButton(text="Open in Kleinanzeigen", url=item_url)
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [open_link_button]
        ]
    )

    return keyboard

# Cancel button
def get_cancel_button() -> InlineKeyboardButton:
    """Create a simple cancel button."""
    return InlineKeyboardButton(text="⬅️ Cancel", callback_data="cancel")
