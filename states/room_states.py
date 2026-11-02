from aiogram.fsm.state import StatesGroup, State

class RoomStates(StatesGroup):
    waiting_room_id = State()
