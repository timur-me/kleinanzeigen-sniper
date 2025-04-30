from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery


from app.bot.keyboards import (
    get_confirm_keyboard,
    get_main_menu,
    get_search_list_keyboard,
    get_search_settings_keyboard,
)
from app.builders.message_builder import SingleSearchMessageBuilder
from app.bot.routers.states import AddSearchStates
from app.db.database import async_session
from app.services import SearchSettingsService

callback_router = Router()



@callback_router.callback_query(F.data.startswith("view_search:"))
async def cb_view_search(callback: CallbackQuery):
    """Handle view_search callback."""
    search_id = callback.data.split(":", 1)[1]
    
    # Get search details
    async with async_session() as session:
        search_settings_service = SearchSettingsService(session)
        search = await search_settings_service.get_by_id(search_id)
    
    if not search:
        await callback.message.edit_text(
            "Search not found. It may have been deleted.",
            reply_markup=await get_search_list_keyboard([])
        )
        await callback.answer()
        return
    
    search_details = SingleSearchMessageBuilder(search)
    
    await callback.message.edit_text(
        search_details.message_text,
        reply_markup=get_search_settings_keyboard(search_id),
        parse_mode="Markdown"
    )
    
    await callback.answer()


@callback_router.callback_query(F.data.startswith("delete_search:"))
async def cb_delete_search(callback: CallbackQuery):
    """Handle delete_search callback."""
    search_id = callback.data.split(":", 1)[1]
    
    await callback.message.edit_text(
        "Are you sure you want to delete this search? This cannot be undone.",
        reply_markup=get_confirm_keyboard("delete", search_id)
    )
    
    await callback.answer()


@callback_router.callback_query(F.data.startswith("confirm_delete:"))
async def cb_confirm_delete(callback: CallbackQuery):
    """Handle confirm_delete callback."""
    search_id = callback.data.split(":", 1)[1]
    
    # Delete the search
    async with async_session() as session:
        search_settings_service = SearchSettingsService(session)
        result = await search_settings_service.delete(search_id)
    
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
        searches = await search_settings_service.get_by_user_id(user_id)
    
    if searches:
        search_ids = [s.id for s in searches]
        
        await callback.message.answer(
            f"You have {len(searches)} saved search{'es' if len(searches) != 1 else ''}. Select one to view details:",
            reply_markup=await get_search_list_keyboard(search_ids)
        )
    else:
        await callback.message.answer(
            "You don't have any saved searches. Use the 'Add Search' button to create one.",
            reply_markup=get_main_menu()
        )
    
    await callback.answer()


@callback_router.callback_query(F.data.startswith("toggle_search:"))
async def cb_toggle_search(callback: CallbackQuery):
    """Handle toggle_search callback."""
    search_id = callback.data.split(":", 1)[1]
    async with async_session() as session:
        search_settings_service = SearchSettingsService(session)
        search = await search_settings_service.get_by_id(search_id)
    
        if not search:
            await callback.message.edit_text(
                "Search not found. It may have been deleted.",
            )
            await callback.answer()
            return
    
        # Toggle status
        await search_settings_service.toggle(search_id)
    
    search_details = SingleSearchMessageBuilder(search)
    
    await callback.message.edit_text(
        search_details.message_text,
        reply_markup=get_search_settings_keyboard(search_id),
        parse_mode="Markdown"
    )
    
    await callback.answer(f"Search status toggled to {'active' if search.is_active else 'inactive'}")


@callback_router.callback_query(F.data == "back_to_searches")
async def cb_back_to_searches(callback: CallbackQuery):
    """Handle back_to_searches callback."""
    user_id = callback.from_user.id
    
    # Get all searches for this user
    async with async_session() as session:
        search_settings_service = SearchSettingsService(session)
        searches = await search_settings_service.get_by_user_id(user_id)
    
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
        reply_markup=await get_search_list_keyboard(search_ids)
    )
    
    await callback.answer()


@callback_router.callback_query(F.data.startswith("search_page:"))
async def cb_search_page(callback: CallbackQuery):
    """Handle search_page callback for pagination."""
    page = int(callback.data.split(":", 1)[1])
    user_id = callback.from_user.id
    
    # Get all searches for this user
    async with async_session() as session:
        search_settings_service = SearchSettingsService(session)
        searches = await search_settings_service.get_by_user_id(user_id)
    
    search_ids = [s.id for s in searches]
    
    await callback.message.edit_text(
        f"You have {len(searches)} saved search{'es' if len(searches) != 1 else ''}. Select one to view details:",
        reply_markup=await get_search_list_keyboard(search_ids, page=page)
    )
    
    await callback.answer()


@callback_router.callback_query(F.data == "cancel")
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

