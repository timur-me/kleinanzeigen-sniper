from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .help import cmd_help

from app.bot.keyboards import (
    get_cancel_keyboard,
    get_main_menu,
    get_search_list_keyboard,
)
from app.services import SearchSettingsService
from app.db.database import async_session
from app.bot.routers.states import AddSearchStates

# Create routers
keyboard_router = Router()

@keyboard_router.message(Command("searches"))
async def cmd_searches(message: Message):
    """Handle /searches command to list user's saved searches."""
    user_id = message.from_user.id
    
    # Get all searches for this user
    async with async_session() as session:
        search_settings_service = SearchSettingsService(session)
        searches = await search_settings_service.get_by_user_id(user_id)
    
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
        reply_markup=await get_search_list_keyboard(search_ids)
    )


@keyboard_router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    """Handle /add command to start adding a new search."""
    await message.answer(
        "🔍 Write search name:",
    )
    
    await state.update_data()
    await state.set_state(AddSearchStates.waiting_for_search_name)


@keyboard_router.message(Command("cancel"))
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
@keyboard_router.message(F.text == "🔍 My Searches")
async def btn_my_searches(message: Message):
    """Handle My Searches button."""
    await cmd_searches(message)


@keyboard_router.message(F.text == "➕ Add Search")
async def btn_add_search(message: Message, state: FSMContext):
    """Handle Add Search button."""
    await cmd_add(message, state)


@keyboard_router.message(F.text == "❓ Help")
async def btn_help(message: Message):
    """Handle Help button."""
    await cmd_help(message)