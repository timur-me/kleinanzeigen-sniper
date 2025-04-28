from aiogram.fsm.state import State, StatesGroup

# Define FSM states for conversation flows
class AddSearchStates(StatesGroup):
    """States for adding a new search."""
    waiting_for_item_name = State()
    waiting_for_location = State()
    waiting_for_location_selection = State()
    waiting_for_radius = State()
    confirmation = State()


class EditSearchStates(StatesGroup):
    """States for editing an existing search."""
    waiting_for_field = State()
    waiting_for_item_name = State()
    waiting_for_location = State()
    waiting_for_location_selection = State()
    waiting_for_radius = State()