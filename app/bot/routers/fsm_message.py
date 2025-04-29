from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message


from app.bot.keyboards import (
    get_cancel_keyboard,
    get_confirm_keyboard,
    get_main_menu,
    get_locations_keyboard
)
from app.db.models import SearchSettings
from app.bot.routers.states import AddSearchStates
from app.kleinanzeigen.kleinanzeigen_client import KleinanzeigenClient
from app.db.database import async_session
from app.services import SearchSettingsService


fsm_router = Router()

# State handlers for adding a search
@fsm_router.message(AddSearchStates.waiting_for_item_name)
async def process_item_name(message: Message, state: FSMContext):
    """Process item name for new search."""
    item_name = message.text.strip()
    
    if not item_name:
        await message.answer("Please enter a valid item name.")
        return
    
    # Save item name in state
    await state.update_data(item_name=item_name)
    
    # Ask for location
    await message.answer(
        "Great! Now enter the location (city or postal code):",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(AddSearchStates.waiting_for_location)


@fsm_router.message(AddSearchStates.waiting_for_location)
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
    
    # await state.set_state(AddSearchStates.waiting_for_location_selection)


@fsm_router.callback_query(F.data.startswith("select_location:"), AddSearchStates.waiting_for_location)
async def process_location_selection(callback: CallbackQuery, state: FSMContext):
    """Process location selection."""
    location_id, location_name = callback.data.split(":")[1:3]

    await state.update_data(location_id=location_id)
    await state.update_data(location_name=location_name)

    await callback.message.edit_text(f"Selected location: {location_name}")

    await callback.message.answer(
        "Now enter the search radius in kilometers (e.g., 10):",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(AddSearchStates.waiting_for_radius)
    



@fsm_router.message(AddSearchStates.waiting_for_radius)
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
    
    # Get all data from state
    data = await state.get_data()
    
    # Show confirmation
    confirmation_text = (
        f"📋 *Search Summary*\n\n"
        f"*Item:* {data['item_name']}\n"
        f"*Location:* {data['location_name']}\n"
        f"*Radius:* {data['radius_km']} km\n\n"
        f"Is this correct? If yes, I'll save this search and start monitoring for new listings."
    )
    
    await message.answer(
        confirmation_text,
        reply_markup=get_confirm_keyboard("add_search", "new"),
        parse_mode="Markdown"
    )
    
    await state.set_state(AddSearchStates.confirmation)


@fsm_router.callback_query(F.data == "confirm_add_search:new", AddSearchStates.confirmation)
async def confirm_add_search(callback: CallbackQuery, state: FSMContext):
    """Handle confirmation of new search addition."""
    # Get data from state
    data = await state.get_data()
    user_id = callback.from_user.id
    
    # Create new search settings
    search = SearchSettings(
        user_id=user_id,
        item_name=data["item_name"],
        location_id=data["location_id"],
        location_name=data["location_name"],
        radius_km=data["radius_km"]
    )
    
    # Save to storage
    async with async_session() as session:
        search_settings_service = SearchSettingsService(session)
        search = await search_settings_service.create(search)
    
    # Clear state
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ Search saved successfully!\n\n"
        f"I'll start monitoring Kleinanzeigen for items matching '{search.item_name}' "
        f"in {search.location_name} (radius: {search.radius_km} km)."
    )
    
    await callback.message.answer(
        "What would you like to do next?",
        reply_markup=get_main_menu()
    )
    
    await callback.answer()


@fsm_router.callback_query(F.data == "cancel_add_search:new", AddSearchStates.confirmation)
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