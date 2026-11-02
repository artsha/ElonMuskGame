from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database.db import get_db

router = Router()

@router.message(Command("deleteroom"))
async def delete_room(message: Message):
    db = await get_db()
    user_id = message.from_user.id
    
    async with db.execute("SELECT room_id FROM rooms WHERE creator_id = ?", (user_id,)) as cursor:
        room = await cursor.fetchone()
    
    if not room:
        await db.close()
        await message.answer("Только создатель может удалить комнату")
        return
    
    room_id = room[0]
    
    await db.execute("DELETE FROM room_members WHERE room_id = ?", (room_id,))
    await db.execute("DELETE FROM problems WHERE room_id = ?", (room_id,))
    await db.execute("DELETE FROM rooms WHERE room_id = ?", (room_id,))
    
    await db.commit()
    await db.close()
    
    await message.answer(f"Комната {room_id} удалена. Игра завершена.")
