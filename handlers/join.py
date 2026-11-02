import random
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command

from database.db import get_db

router = Router()

@router.message(Command("join"))
async def join_room(message: Message):
    args = message.text.split()
    if len(args) < 2:
        await message.answer("Использование: /join ROOM_ID")
        return
    
    room_id = args[1].upper()
    db = await get_db()
    user_id = message.from_user.id
    
    await db.execute("INSERT OR IGNORE INTO users (user_id, username, full_name) VALUES (?, ?, ?)",
                     (user_id, message.from_user.username, message.from_user.full_name))
    
    async with db.execute("SELECT status FROM rooms WHERE room_id = ?", (room_id,)) as cursor:
        room = await cursor.fetchone()
    
    if not room:
        await db.close()
        await message.answer("Комната не найдена")
        return
    
    await db.execute("INSERT OR IGNORE INTO room_members (room_id, user_id) VALUES (?, ?)", (room_id, user_id))
    await db.commit()
    await db.close()
    
    await message.answer(f"Ты присоединился к комнате {room_id}\nУправление: /room")
