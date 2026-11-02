from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from database.db import get_db
from states.room_states import RoomStates

router = Router()

@router.message(Command("create"))
async def create_room_start(message: Message, state: FSMContext):
    await state.set_state(RoomStates.waiting_room_id)
    await message.answer("Введи ID комнаты, который хочешь использовать.\n\nID должен быть уникальным.")

@router.message(RoomStates.waiting_room_id)
async def create_room_finish(message: Message, state: FSMContext):
    db = await get_db()
    user_id = message.from_user.id
    room_id = message.text.strip().upper()
    
    if len(room_id) < 3 or len(room_id) > 16:
        await db.close()
        await message.answer("ID комнаты должен быть от 3 до 16 символов")
        return
    
    await db.execute("INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
                     (user_id, message.from_user.username, message.from_user.full_name))
    
    async with db.execute("SELECT room_id FROM rooms WHERE room_id = ?", (room_id,)) as cursor:
        exists = await cursor.fetchone()
    
    if exists:
        await db.close()
        await message.answer("Такая комната уже существует. Введи другой ID.")
        return
    
    await db.execute("INSERT INTO rooms (room_id, creator_id) VALUES (?, ?)", (room_id, user_id))
    await db.execute("INSERT INTO room_members (room_id, user_id) VALUES (?, ?)", (room_id, user_id))
    await db.commit()
    await db.close()
    await state.clear()
    
    await message.answer(
        f"Комната создана!\n\n"
        f"ID комнаты: {room_id}\n"
        f"Ты - создатель (администратор)\n\n"
        f"Отправь этот ID другим игрокам, чтобы они присоединились.\n"
        f"Управление: /room"
    )
