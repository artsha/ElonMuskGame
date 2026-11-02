from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from database.db import get_db

router = Router()

@router.message(Command("players"))
async def show_players(message: Message):
    db = await get_db()
    user_id = message.from_user.id
    
    async with db.execute("""
        SELECT r.room_id 
        FROM rooms r 
        JOIN room_members rm ON r.room_id = rm.room_id 
        WHERE rm.user_id = ? 
        ORDER BY rm.joined_at DESC LIMIT 1
    """, (user_id,)) as cursor:
        room = await cursor.fetchone()
    
    if not room:
        await db.close()
        await message.answer("Ты не состоишь ни в одной комнате\n/create - создать\n/join ID - присоединиться")
        return
    
    room_id = room[0]
    
    async with db.execute("""
        SELECT u.user_id, u.full_name, u.username
        FROM room_members rm
        JOIN users u ON rm.user_id = u.user_id
        WHERE rm.room_id = ?
        ORDER BY rm.joined_at ASC
    """, (room_id,)) as cursor:
        members = await cursor.fetchall()
    
    await db.close()
    
    text = f"Игроки в комнате {room_id} ({len(members)}):\n\n"
    for i, member in enumerate(members, 1):
        user_id_m, full_name, username = member
        if username:
            text += f"{i}. {full_name} (@{username})\n"
        else:
            text += f"{i}. {full_name}\n"
    
    await message.answer(text)
