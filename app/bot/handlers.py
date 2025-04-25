from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import CallbackQuery, Message
from loguru import logger

from app.bot.keyboards import (
    get_cancel_keyboard,
    get_confirm_keyboard,
    get_main_menu,
    get_search_list_keyboard,
    get_search_settings_keyboard,
)
from app.config.settings import settings
from app.models.models import SearchSettings, User
from app.services.storage import search_settings_storage, user_storage

# Create routers
router = Router()


# Define FSM states for conversation flows
class AddSearchStates(StatesGroup):
    """States for adding a new search."""
    waiting_for_item_name = State()
    waiting_for_location = State()
    waiting_for_radius = State()
    confirmation = State()


class EditSearchStates(StatesGroup):
    """States for editing an existing search."""
    waiting_for_field = State()
    waiting_for_item_name = State()
    waiting_for_location = State()
    waiting_for_radius = State()


# Command handlers
@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handle /start command."""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    last_name = message.from_user.last_name
    
    # Check if user already exists
    existing_user = user_storage.get_by_id(user_id)
    
    if not existing_user:
        # Create new user
        is_admin = user_id in settings.ADMIN_USER_IDS
        
        user = User(
            user_id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            is_admin=is_admin
        )
        
        user_storage.save(user)
        logger.info(f"New user registered: {user.full_name()} (ID: {user_id})")
    else:
        # Update existing user data
        existing_user.username = username
        existing_user.first_name = first_name
        existing_user.last_name = last_name
        user_storage.save(existing_user)
    
    # Welcome message
    await message.answer(
        f"Welcome to Kleinanzeigen Sniper, {first_name or username or 'there'}! 👋\n\n"
        f"This bot helps you monitor Kleinanzeigen.de for new listings matching your search criteria.\n\n"
        f"Use the menu below to get started or type /help for more information.",
        reply_markup=get_main_menu()
    )


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command."""
    help_text = (
        "📚 *Kleinanzeigen Sniper Help* 📚\n\n"
        "*Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/searches - View your saved searches\n"
        "/add - Add a new search\n"
        "/cancel - Cancel current operation\n\n"
        
        "*How to use:*\n"
        "1. Add a search with an item name, location, and radius\n"
        "2. The bot will periodically check for new listings\n"
        "3. When new items are found, you'll receive notifications\n"
        "4. Manage your searches at any time\n\n"
        
        "*Tips:*\n"
        "• Be specific with item names for better results\n"
        "• Set a reasonable radius based on how far you're willing to travel\n"
        "• You can have multiple active searches at once"
    )
    
    await message.answer(help_text, parse_mode="Markdown")


@router.message(Command("searches"))
async def cmd_searches(message: Message):
    """Handle /searches command to list user's saved searches."""
    user_id = message.from_user.id
    
    # Get all searches for this user
    searches = search_settings_storage.get_by_user_id(user_id)
    
    if not searches:
        await message.answer(
            "You don't have any saved searches yet. Use the 'Add Search' button or /add command to create one.",
            reply_markup=get_main_menu()
        )
        return
    
    # Display searches with pagination
    search_ids = [s.id for s in searches]
    
    await message.answer(
        f"You have {len(searches)} saved search{'es' if len(searches) != 1 else ''}. Select one to view details:",
        reply_markup=get_search_list_keyboard(search_ids)
    )


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    """Handle /add command to start adding a new search."""
    await message.answer(
        "Let's add a new search! What item are you looking for?",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(AddSearchStates.waiting_for_item_name)


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Handle /cancel command to cancel current operation."""
    current_state = await state.get_state()
    
    if current_state is None:
        await message.answer(
            "Nothing to cancel. You're not in the middle of any operation.",
            reply_markup=get_main_menu()
        )
        return
    
    await state.clear()
    await message.answer(
        "Operation cancelled. What would you like to do next?",
        reply_markup=get_main_menu()
    )


# Button handlers
@router.message(F.text == "🔍 My Searches")
async def btn_my_searches(message: Message):
    """Handle My Searches button."""
    await cmd_searches(message)


@router.message(F.text == "➕ Add Search")
async def btn_add_search(message: Message, state: FSMContext):
    """Handle Add Search button."""
    await cmd_add(message, state)


@router.message(F.text == "❓ Help")
async def btn_help(message: Message):
    """Handle Help button."""
    await cmd_help(message)


@router.message(F.text == "⚙️ Settings")
async def btn_settings(message: Message):
    """Handle Settings button."""
    await message.answer(
        "Settings functionality is coming soon! Stay tuned for updates.",
        reply_markup=get_main_menu()
    )


# Callback query handlers (for inline keyboards)
@router.callback_query(F.data == "add_search")
async def cb_add_search(callback: CallbackQuery, state: FSMContext):
    """Handle add_search callback."""
    await callback.message.edit_text(
        "Let's add a new search! What item are you looking for?",
    )
    
    await state.set_state(AddSearchStates.waiting_for_item_name)
    await callback.answer()


@router.callback_query(F.data.startswith("view_search:"))
async def cb_view_search(callback: CallbackQuery):
    """Handle view_search callback."""
    search_id = callback.data.split(":", 1)[1]
    
    # Get search details
    search = search_settings_storage.get_by_id(search_id)
    
    if not search:
        await callback.message.edit_text(
            "Search not found. It may have been deleted.",
            reply_markup=get_search_list_keyboard([])
        )
        await callback.answer()
        return
    
    # Format search details
    status = "✅ Active" if search.is_active else "❌ Inactive"
    
    search_details = (
        f"📊 *Search Details*\n\n"
        f"*Item:* {search.item_name}\n"
        f"*Location:* {search.location}\n"
        f"*Radius:* {search.radius_km} km\n"
        f"*Status:* {status}\n"
        f"*Created:* {search.created_at.strftime('%Y-%m-%d')}"
    )
    
    await callback.message.edit_text(
        search_details,
        reply_markup=get_search_settings_keyboard(search_id),
        parse_mode="Markdown"
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith("delete_search:"))
async def cb_delete_search(callback: CallbackQuery):
    """Handle delete_search callback."""
    search_id = callback.data.split(":", 1)[1]
    
    await callback.message.edit_text(
        "Are you sure you want to delete this search? This cannot be undone.",
        reply_markup=get_confirm_keyboard("delete", search_id)
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete:"))
async def cb_confirm_delete(callback: CallbackQuery):
    """Handle confirm_delete callback."""
    search_id = callback.data.split(":", 1)[1]
    
    # Delete the search
    result = search_settings_storage.delete(search_id)
    
    if result:
        await callback.message.edit_text(
            "Search has been deleted successfully."
        )
    else:
        await callback.message.edit_text(
            "Error deleting search. It may have already been deleted.",
        )
    
    # Get updated search list for this user
    user_id = callback.from_user.id
    searches = search_settings_storage.get_by_user_id(user_id)
    
    if searches:
        search_ids = [s.id for s in searches]
        
        await callback.message.answer(
            f"You have {len(searches)} saved search{'es' if len(searches) != 1 else ''}. Select one to view details:",
            reply_markup=get_search_list_keyboard(search_ids)
        )
    else:
        await callback.message.answer(
            "You don't have any saved searches. Use the 'Add Search' button to create one.",
            reply_markup=get_main_menu()
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("toggle_search:"))
async def cb_toggle_search(callback: CallbackQuery):
    """Handle toggle_search callback."""
    search_id = callback.data.split(":", 1)[1]
    
    # Get search
    search = search_settings_storage.get_by_id(search_id)
    
    if not search:
        await callback.message.edit_text(
            "Search not found. It may have been deleted.",
        )
        await callback.answer()
        return
    
    # Toggle status
    search.is_active = not search.is_active
    search_settings_storage.save(search)
    
    # Format updated search details
    status = "✅ Active" if search.is_active else "❌ Inactive"
    
    search_details = (
        f"📊 *Search Details*\n\n"
        f"*Item:* {search.item_name}\n"
        f"*Location:* {search.location}\n"
        f"*Radius:* {search.radius_km} km\n"
        f"*Status:* {status}\n"
        f"*Created:* {search.created_at.strftime('%Y-%m-%d')}"
    )
    
    await callback.message.edit_text(
        search_details,
        reply_markup=get_search_settings_keyboard(search_id),
        parse_mode="Markdown"
    )
    
    await callback.answer(f"Search status toggled to {'active' if search.is_active else 'inactive'}")


@router.callback_query(F.data == "back_to_searches")
async def cb_back_to_searches(callback: CallbackQuery):
    """Handle back_to_searches callback."""
    user_id = callback.from_user.id
    
    # Get all searches for this user
    searches = search_settings_storage.get_by_user_id(user_id)
    
    if not searches:
        await callback.message.edit_text(
            "You don't have any saved searches yet. Use the 'Add Search' button to create one.",
        )
        await callback.answer()
        return
    
    # Display searches with pagination
    search_ids = [s.id for s in searches]
    
    await callback.message.edit_text(
        f"You have {len(searches)} saved search{'es' if len(searches) != 1 else ''}. Select one to view details:",
        reply_markup=get_search_list_keyboard(search_ids)
    )
    
    await callback.answer()


@router.callback_query(F.data.startswith("search_page:"))
async def cb_search_page(callback: CallbackQuery):
    """Handle search_page callback for pagination."""
    page = int(callback.data.split(":", 1)[1])
    user_id = callback.from_user.id
    
    # Get all searches for this user
    searches = search_settings_storage.get_by_user_id(user_id)
    search_ids = [s.id for s in searches]
    
    await callback.message.edit_text(
        f"You have {len(searches)} saved search{'es' if len(searches) != 1 else ''}. Select one to view details:",
        reply_markup=get_search_list_keyboard(search_ids, page=page)
    )
    
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cb_cancel(callback: CallbackQuery, state: FSMContext):
    """Handle cancel callback."""
    current_state = await state.get_state()
    
    if current_state is not None:
        await state.clear()
    
    await callback.message.edit_text(
        "Operation cancelled. Use the buttons below to continue.",
        reply_markup=None
    )
    
    await callback.message.answer(
        "What would you like to do next?",
        reply_markup=get_main_menu()
    )
    
    await callback.answer()


# State handlers for adding a search
@router.message(AddSearchStates.waiting_for_item_name)
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


@router.message(AddSearchStates.waiting_for_location)
async def process_location(message: Message, state: FSMContext):
    """Process location for new search."""
    location = message.text.strip()
    
    if not location:
        await message.answer("Please enter a valid location.")
        return
    
    # Save location in state
    await state.update_data(location=location)
    
    # Ask for radius
    await message.answer(
        "Now enter the search radius in kilometers (e.g., 10):",
        reply_markup=get_cancel_keyboard()
    )
    
    await state.set_state(AddSearchStates.waiting_for_radius)


@router.message(AddSearchStates.waiting_for_radius)
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
        f"*Location:* {data['location']}\n"
        f"*Radius:* {data['radius_km']} km\n\n"
        f"Is this correct? If yes, I'll save this search and start monitoring for new listings."
    )
    
    await message.answer(
        confirmation_text,
        reply_markup=get_confirm_keyboard("add_search", "new"),
        parse_mode="Markdown"
    )
    
    await state.set_state(AddSearchStates.confirmation)


@router.callback_query(F.data == "confirm_add_search:new", AddSearchStates.confirmation)
async def confirm_add_search(callback: CallbackQuery, state: FSMContext):
    """Handle confirmation of new search addition."""
    # Get data from state
    data = await state.get_data()
    user_id = callback.from_user.id
    
    # Create new search settings
    search = SearchSettings(
        user_id=user_id,
        item_name=data["item_name"],
        location=data["location"],
        radius_km=data["radius_km"]
    )
    
    # Save to storage
    search_settings_storage.save(search)
    
    # Clear state
    await state.clear()
    
    await callback.message.edit_text(
        f"✅ Search saved successfully!\n\n"
        f"I'll start monitoring Kleinanzeigen for items matching '{search.item_name}' "
        f"in {search.location} (radius: {search.radius_km} km)."
    )
    
    await callback.message.answer(
        "What would you like to do next?",
        reply_markup=get_main_menu()
    )
    
    await callback.answer()


@router.callback_query(F.data == "cancel_add_search:new", AddSearchStates.confirmation)
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