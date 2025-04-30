from uuid import uuid4
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from app.db.models import SearchSettings
from app.kleinanzeigen.kleinanzeigen_client import KleinanzeigenClient
from app.services import UserService

from app.bot.keyboards import (
    get_cancel_keyboard,
    get_locations_keyboard,
    get_main_menu,
)
from app.bot.routers.states import AddSearchStates
from app.db.database import async_session
from app.services import SearchSettingsService

search_create_router = Router()

test_map = {
    "button_text": {
        "alias": "Change alias",
        "item_name": "Change item name",
        "lowest_price": "Change lowest price",
        "highest_price": "Change highest price",
        "location": "Change location",
        "radius": "Change radius",
    },
    "prompt": {
        "alias": "🔍 Enter search alias:",
        "item_name": "✏️ Enter new item name:",
        "lowest_price": "💰 Enter new lowest price:",
        "highest_price": "💸 Enter new highest price:",
        "location": "📍 Enter location (city or postal code):",
        "radius": "📏 Enter search radius in km:",
    },
    "state": {
        "alias": AddSearchStates.waiting_for_search_name,
        "item_name": AddSearchStates.waiting_for_item_name,
        "lowest_price": AddSearchStates.waiting_for_lowest_price,
        "highest_price": AddSearchStates.waiting_for_highest_price,
        "location": AddSearchStates.waiting_for_location,
        "radius": AddSearchStates.waiting_for_radius,
    }
}

async def confirmation_message(state: FSMContext, user_id: int):
    """Build confirmation message."""
    if not state:
        return 
    
    data = await state.get_data()
    search_name = data.get("search_name")
    item_name = data.get("item_name")
    lowest_price = data.get("lowest_price")
    highest_price = data.get("highest_price")
    location_name = data.get("location_name")
    radius_km = data.get("radius_km")
    ad_type = data.get("ad_type")
    poster_type = data.get("poster_type")
    is_picture_required = data.get("is_picture_required")

    async with async_session() as session:
        user_service = UserService(session)
        user_settings = await user_service.get_user_settings(user_id)

        ad_type = ad_type or user_settings.default_ad_type
        poster_type = poster_type or user_settings.default_poster_type
        is_picture_required = is_picture_required or user_settings.default_is_picture_required
    
    message_text = f"""
🔍 *Search name:* `{search_name}`
✏️ *Item name:* `{item_name}`

💶 *Price range:* `{lowest_price or user_settings.default_lowest_price}` – `{highest_price or user_settings.default_highest_price}` EUR  
🔍 *Location:* `{location_name or user_settings.default_location_name}` (+{radius_km or user_settings.default_location_radius_km} km)

🔖 *Ad type:* _{ad_type.value.capitalize() if ad_type else "Any"}_
👤 *Poster type:* _{poster_type.value.capitalize() if poster_type else "Any"}_
📷 *Photos required:* {"✅ Yes" if is_picture_required else "❌ No"}
"""


    inline_keyboard = []
    for key, value in test_map["button_text"].items():
        inline_keyboard.append([InlineKeyboardButton(text=value, callback_data=f"add_search_edit:{key}")])

    inline_keyboard.append([InlineKeyboardButton(text="Add", callback_data=f"add_search_confirm")])
    inline_keyboard.append([InlineKeyboardButton(text="Cancel", callback_data=f"add_search_cancel")])

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard
    )

    return message_text, keyboard

    

# Callback query handlers (for inline keyboards)
@search_create_router.callback_query(F.data == "add_search")
async def cb_add_search(callback: CallbackQuery, state: FSMContext):
    """Handle add_search callback."""
    await callback.message.edit_text(
        "🔍 Write search name:",
    )
    
    await state.update_data()
    await state.set_state(AddSearchStates.waiting_for_search_name)
    await callback.answer()

@search_create_router.message(AddSearchStates.waiting_for_search_name)
async def creating_search_name(message: Message, state: FSMContext):
    """Handle creating search name."""
    if not message.text:
        await message.answer("Please enter a valid search name.")
        return
    
    await state.update_data(search_name=message.text)
    await state.set_state(AddSearchStates.waiting_for_item_name)
    await message.answer("✏️ Now write item name to search:")

@search_create_router.message(AddSearchStates.waiting_for_item_name)
async def creating_search_item_name(message: Message, state: FSMContext):
    """Handle creating search item name."""
    if not message.text:
        await message.answer("Please enter a valid item name.")
        return
    
    await state.update_data(item_name=message.text)
    await state.set_state(AddSearchStates.hold)
    text, keyboard = await confirmation_message(state, message.from_user.id)

    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

@search_create_router.callback_query(F.data.startswith("add_search_edit:"), AddSearchStates.hold)
async def handle_edit_field(callback: CallbackQuery, state: FSMContext):
    _, field = callback.data.split(":")
    await state.set_state(test_map["state"][field])
    await callback.message.edit_text(test_map["prompt"][field], reply_markup=get_cancel_keyboard())
    await callback.answer()

@search_create_router.message(AddSearchStates.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    """Process location for new search."""
    location_query = message.text.strip()
    
    if not location_query:
        await message.answer("Please enter a valid location.")
        return
    
    locations = await KleinanzeigenClient.get_instance().fetch_locations(location_query)
    if not locations:
        await message.answer("No locations found. Please try again.")
        return
    
    await message.answer(
        "Please select the location from the list or write a new location:",
        reply_markup=get_locations_keyboard(locations)
    )


@search_create_router.callback_query(F.data.startswith("select_location:"), AddSearchStates.waiting_for_location)
async def process_location_selection(callback: CallbackQuery, state: FSMContext):
    """Process location selection."""
    location_id, location_name = callback.data.split(":")[1:3]

    await state.update_data(location_id=location_id)
    await state.update_data(location_name=location_name)

    await callback.message.edit_text(f"Selected location: {location_name}")
    await state.set_state(AddSearchStates.hold)

    text, keyboard = await confirmation_message(state, callback.from_user.id)
    await callback.message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

    await callback.answer()


@search_create_router.message(AddSearchStates.waiting_for_radius)
async def process_radius(message: Message, state: FSMContext):
    """Process radius for new search."""
    radius_text = message.text.strip()
    
    try:
        radius = int(radius_text)
        if radius < 0:
            raise ValueError("Radius must be positive")
    except ValueError:
        await message.answer("Please enter a valid number for the radius.")
        return
    
    # Save radius in state
    await state.update_data(radius_km=radius)
    await state.set_state(AddSearchStates.hold)
    
    text, keyboard = await confirmation_message(state, message.from_user.id)
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")

@search_create_router.message(AddSearchStates.waiting_for_lowest_price)
async def process_lowest_price(message: Message, state: FSMContext):
    """Process lowest price for new search."""
    price_text = message.text.strip()
    
    try:
        price = int(price_text)
        if price < 0:
            raise ValueError("Price must be positive")
    except ValueError:
        await message.answer("Please enter a valid number for the price.")
        return
    
    await state.update_data(lowest_price=price)
    await state.set_state(AddSearchStates.hold)
    text, keyboard = await confirmation_message(state, message.from_user.id)
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")


@search_create_router.message(AddSearchStates.waiting_for_highest_price)
async def process_highest_price(message: Message, state: FSMContext):
    """Process highest price for new search."""
    price_text = message.text.strip()
    
    try:
        price = int(price_text)
        if price < 0:
            raise ValueError("Price must be positive")
    except ValueError:
        await message.answer("Please enter a valid number for the price.")
        return

    await state.update_data(highest_price=price)
    await state.set_state(AddSearchStates.hold)
    text, keyboard = await confirmation_message(state, message.from_user.id)
    await message.answer(text, reply_markup=keyboard, parse_mode="Markdown")



@search_create_router.callback_query(F.data == "add_search_confirm", AddSearchStates.hold)
async def confirm_add_search(callback: CallbackQuery, state: FSMContext):
    """Handle confirmation of new search addition."""
    # Get data from state
    data = await state.get_data()
    user_id = callback.from_user.id

    async with async_session() as session:
        user_service = UserService(session)
        user_settings = await user_service.get_user_settings(user_id)

        search_name = data.get("search_name")
        item_name = data.get("item_name")
        lowest_price = data.get("lowest_price") or user_settings.default_lowest_price
        highest_price = data.get("highest_price") or user_settings.default_highest_price
        location_name = data.get("location_name") or user_settings.default_location_name
        location_id = data.get("location_id") or user_settings.default_location_id
        radius_km = data.get("radius_km") or user_settings.default_location_radius_km
        ad_type = data.get("ad_type") or user_settings.default_ad_type
        poster_type = data.get("poster_type") or user_settings.default_poster_type
        is_picture_required = data.get("is_picture_required") or user_settings.default_is_picture_required

        
        # Create new search settings
        search = SearchSettings(
            user_id=user_id,
            alias=search_name,
            item_name=item_name,
            lowest_price=lowest_price,
            highest_price=highest_price,
            location_id=location_id,
            location_name=location_name,
            radius_km=radius_km,
            ad_type=ad_type,
            poster_type=poster_type,
            is_picture_required=is_picture_required
        )

        search_settings_service = SearchSettingsService(session)
        search = await search_settings_service.create(search)
    
    # Clear state
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ Search saved successfully!\n\n"
        f"I'll start monitoring Kleinanzeigen with search {search_name} "
    )
    
    await callback.message.answer(
        "What would you like to do next?",
        reply_markup=get_main_menu()
    )
    
    await callback.answer()


@search_create_router.callback_query(F.data == "add_search_cancel", AddSearchStates.hold)
async def cancel_add_search(callback: CallbackQuery, state: FSMContext):
    """Handle cancellation of new search addition."""
    await state.clear()
    
    await callback.message.edit_text(
        "Search creation cancelled. No search was saved."
    )
    
    await callback.message.answer(
        "What would you like to do next?",
        reply_markup=get_main_menu()
    )
    
    await callback.answer() 